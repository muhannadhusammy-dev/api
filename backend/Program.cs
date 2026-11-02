using System.Security.Claims;
using System.Text.Json;
using Microsoft.AspNetCore.Authentication;
using Microsoft.AspNetCore.Authentication.Cookies;
using Microsoft.AspNetCore.Identity;
using Microsoft.EntityFrameworkCore;
using TajerOS;

var b = WebApplication.CreateBuilder(args);
b.WebHost.UseUrls(b.Configuration["Urls"] ?? "http://127.0.0.1:5082");
b.WebHost.ConfigureKestrel(o => o.Limits.MaxRequestBodySize = 12_000_000);
b.Services.AddDbContext<AppDb>(o => { var pg = b.Configuration.GetConnectionString("Postgres"); if (!string.IsNullOrWhiteSpace(pg)) o.UseNpgsql(pg); else o.UseSqlite(b.Configuration.GetConnectionString("Sqlite") ?? "Data Source=tajeros.db"); });
b.Services.AddSingleton<WriteGate>(); b.Services.AddSingleton<OpsMonitor>();
b.Services.AddHttpClient("ai", c => { c.BaseAddress = new Uri(b.Configuration["AI_URL"] ?? "http://127.0.0.1:8091"); c.Timeout = TimeSpan.FromSeconds(180); });
b.Services.AddAuthentication(CookieAuthenticationDefaults.AuthenticationScheme).AddCookie(o => { o.Cookie.Name = "TajerOS.Session"; o.Cookie.HttpOnly = true; o.Cookie.SameSite = SameSiteMode.Strict; o.ExpireTimeSpan = TimeSpan.FromHours(4); o.Events.OnRedirectToLogin = c => { c.Response.StatusCode = 401; return Task.CompletedTask; }; o.Events.OnRedirectToAccessDenied = c => { c.Response.StatusCode = 403; return Task.CompletedTask; }; });
b.Services.AddAuthorization(o => o.AddPolicy("owner", p => p.RequireRole("owner")));
var app = b.Build();
using (var scope = app.Services.CreateScope())
{
    var db = scope.ServiceProvider.GetRequiredService<AppDb>(); await db.Database.EnsureCreatedAsync();
    if (!await db.Operators.AnyAsync())
    {
        var user = new Operator { Email = "owner@tajer.local", Role = "owner" }; user.PasswordHash = new PasswordHasher<Operator>().HashPassword(user, b.Configuration["DEMO_PASSWORD"] ?? "TajerDemo!2026"); db.Operators.Add(user);
        var staff = new Operator { Email = "staff@tajer.local", Role = "staff" }; staff.PasswordHash = new PasswordHasher<Operator>().HashPassword(staff, b.Configuration["DEMO_PASSWORD"] ?? "TajerDemo!2026"); db.Operators.Add(staff);
    }
    if (!await db.Products.AnyAsync()) db.Products.AddRange(new Product { Id = "oil", Name = "Cooking oil", ArabicName = "زيت", Stock = 0, AverageCost = 0 }, new Product { Id = "rice", Name = "Rice", ArabicName = "أرز", Stock = 25, AverageCost = 180, ReorderPoint = 8 }, new Product { Id = "sugar", Name = "Sugar", ArabicName = "سكر", Stock = 18, AverageCost = 150, ReorderPoint = 6 });
    if (!await db.Documents.AnyAsync()) db.Documents.AddRange(new BusinessDocument { Title = "Returns policy / سياسة المرتجعات", Text = "Customers may return unopened goods within 14 days with the original receipt. Owner approval is required before any refund or inventory adjustment. يسمح بإرجاع المنتجات غير المفتوحة خلال 14 يومًا مع الفاتورة الأصلية. يلزم اعتماد المالك قبل رد الأموال أو تعديل المخزون." }, new BusinessDocument { Title = "Purchasing policy / سياسة المشتريات", Text = "Purchase orders above EGP 5000 require owner approval. Check quantities, pack units and supplier totals before posting inventory. المشتريات فوق 5000 جنيه تحتاج موافقة المالك. راجع الكمية والوحدة وإجمالي المورد قبل ترحيل المخزون." }, new BusinessDocument { Title = "Oil replenishment / إعادة طلب الزيت", Text = "Cooking oil supplier lead time is three days. Maintain a safety stock of 10 cartons. Review supplier availability before ordering. مدة توريد الزيت ثلاثة أيام ومخزون الأمان 10 كراتين. تأكد من توفر البضاعة عند المورد قبل الطلب." });
    await db.SaveChangesAsync();
}
app.Use(async (c, next) =>
{
    var timer = System.Diagnostics.Stopwatch.StartNew();
    try { await next(); } finally { if (c.Request.Path.StartsWithSegments("/api") && !c.Request.Path.StartsWithSegments("/api/ops")) c.RequestServices.GetRequiredService<OpsMonitor>().Record(c.Request.Path, c.Response.StatusCode, timer.Elapsed.TotalMilliseconds); else if (c.Request.Path.Value?.Contains("simulate-failure") == true) c.RequestServices.GetRequiredService<OpsMonitor>().Record(c.Request.Path, c.Response.StatusCode, timer.Elapsed.TotalMilliseconds); }
});
app.Use(async (c, next) =>
{
    c.Response.Headers["X-Content-Type-Options"] = "nosniff"; c.Response.Headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; connect-src 'self'; media-src 'self' blob:; frame-ancestors 'none'";
    if (c.Request.Path.StartsWithSegments("/api") && c.Request.Method != "GET" && c.Request.Method != "HEAD")
    {
        if (c.Request.Headers["X-Tajer-Request"] != "1") { c.Response.StatusCode = 400; await c.Response.WriteAsJsonAsync(new { error = "Missing application request header." }); return; }
        if (c.Request.Headers.TryGetValue("Origin", out var origin) && Uri.TryCreate(origin.ToString(), UriKind.Absolute, out var u) && u.Authority != c.Request.Host.Value) { c.Response.StatusCode = 403; return; }
    }
    try { await next(); } catch (DbUpdateConcurrencyException) { c.Response.StatusCode = 409; await c.Response.WriteAsJsonAsync(new { error = "Record changed. Reload before approving." }); } catch (HttpRequestException) { c.Response.StatusCode = 503; await c.Response.WriteAsJsonAsync(new { error = "AI service unavailable. Start the Python AI service; no business records changed." }); } catch (Exception ex) { app.Logger.LogError(ex, "Request failed"); if (!c.Response.HasStarted) { c.Response.StatusCode = 500; await c.Response.WriteAsJsonAsync(new { error = "Operation failed. No approval was reported successful. Check server logs." }); } }
});
app.UseDefaultFiles(); app.UseStaticFiles(); app.UseAuthentication(); app.UseAuthorization();
string Actor(HttpContext c) => c.User.Identity?.Name ?? "unknown";
void Audit(AppDb db, HttpContext c, string action, object id) => db.Audits.Add(new Audit { Actor = Actor(c), Action = action, EntityId = id.ToString() ?? "" });
async Task<JsonElement> AI(IHttpClientFactory factory, string path, object data) { var r = await factory.CreateClient("ai").PostAsJsonAsync(path, data); r.EnsureSuccessStatusCode(); return await r.Content.ReadFromJsonAsync<JsonElement>(); }
app.MapGet("/api/health", () => new { status = "ok", app = "TajerOS AI", backend = "ASP.NET Core 10", database = string.IsNullOrWhiteSpace(b.Configuration.GetConnectionString("Postgres")) ? "SQLite demo" : "PostgreSQL" });
app.MapPost("/api/login", async (Login input, AppDb db, HttpContext c) =>
{
    if (string.IsNullOrWhiteSpace(input.Email) || string.IsNullOrEmpty(input.Password) || input.Email.Length > 254 || input.Password.Length > 1024) return Results.BadRequest(new { error = "Email and password are required." });
    var user = await db.Operators.SingleOrDefaultAsync(x => x.Email == input.Email);
    if (user is null || new PasswordHasher<Operator>().VerifyHashedPassword(user, user.PasswordHash, input.Password) == PasswordVerificationResult.Failed) return Results.Unauthorized();
    await c.SignInAsync(new ClaimsPrincipal(new ClaimsIdentity(new[] { new Claim(ClaimTypes.Name, user.Email), new Claim(ClaimTypes.Role, user.Role) }, CookieAuthenticationDefaults.AuthenticationScheme))); return Results.Ok(new { email = user.Email, role = user.Role });
});
app.MapPost("/api/logout", async (HttpContext c) => { await c.SignOutAsync(); return Results.Ok(); }).RequireAuthorization();
app.MapGet("/api/me", (HttpContext c) => new { email = Actor(c), role = c.User.FindFirstValue(ClaimTypes.Role) }).RequireAuthorization();
app.MapGet("/api/dashboard", async (AppDb db) =>
{
    var products = await db.Products.ToListAsync(); var ledger = await db.Ledger.ToListAsync(); decimal revenue = ledger.Where(x => x.Kind == "sale").Sum(x => x.Total) - ledger.Where(x => x.Kind == "return").Sum(x => x.Total); decimal cogs = ledger.Where(x => x.Kind == "sale").Sum(x => x.Cost) - ledger.Where(x => x.Kind == "return").Sum(x => x.Cost);
    return new { products, proposals = await db.Proposals.OrderByDescending(x => x.CreatedAt).Take(50).ToListAsync(), ledger = ledger.OrderByDescending(x => x.CreatedAt).Take(50), workflows = await db.Workflows.ToListAsync(), workflowRecords = await db.WorkflowRecords.OrderByDescending(x => x.CreatedAt).Take(50).ToListAsync(), documents = await db.Documents.Select(x => new { x.Id, x.Title, x.Source }).ToListAsync(), revenue, cogs, grossProfit = revenue - cogs, inventoryValue = products.Sum(x => x.Stock * x.AverageCost), note = "Gross profit excludes expenses and tax. Seeded rice/sugar opening balances are demo assumptions." };
}).RequireAuthorization();
app.MapPost("/api/commands/propose", async (Command input, AppDb db, IHttpClientFactory f, HttpContext c) =>
{
    if (string.IsNullOrWhiteSpace(input.Text) || input.Text.Length > 4000 || string.IsNullOrWhiteSpace(input.RequestKey) || input.RequestKey.Length > 100) return Results.BadRequest(new { error = "Text and requestKey are required." });
    var existing = await db.Proposals.Where(x => x.RequestKey.StartsWith(input.RequestKey + ":")).ToListAsync(); if (existing.Count > 0) return Results.Ok(new { proposals = existing, duplicate = true });
    var ai = await AI(f, "/interpret", new { text = input.Text }); var added = new List<Proposal>(); int i = 0;
    foreach (var a in ai.GetProperty("actions").EnumerateArray())
    {
        string pid = a.GetProperty("productId").GetString() ?? ""; if (!await db.Products.AnyAsync(x => x.Id == pid)) continue;
        var p = new Proposal { Kind = a.GetProperty("kind").GetString()!, ProductId = pid, Quantity = a.GetProperty("quantity").GetDecimal(), Total = a.TryGetProperty("total", out var t) && t.ValueKind == JsonValueKind.Number ? t.GetDecimal() : null, Source = input.Text, Warnings = a.GetProperty("warning").GetString() ?? "", CreatedBy = Actor(c), RequestKey = input.RequestKey + ":" + i++ };
        if (p.Kind is not ("purchase" or "sale") || p.Quantity <= 0 || p.Quantity > 1000000) continue; db.Proposals.Add(p); added.Add(p); Audit(db, c, "proposal.created", p.Id);
    }
    await db.SaveChangesAsync(); return Results.Ok(new { proposals = added, interpretation = ai });
}).RequireAuthorization();
app.MapPost("/api/proposals", async (ManualProposal r, AppDb db, HttpContext c) =>
{
    if (r.Kind is not ("purchase" or "sale") || r.Quantity <= 0 || r.Quantity > 1000000 || r.Total < 0 || r.Total > 1000000000 || string.IsNullOrWhiteSpace(r.RequestKey) || r.RequestKey.Length > 100 || !await db.Products.AnyAsync(x => x.Id == r.ProductId)) return Results.BadRequest(new { error = "Invalid transaction fields." });
    var old = await db.Proposals.SingleOrDefaultAsync(x => x.RequestKey == r.RequestKey); if (old is not null) return Results.Ok(old);
    var p = new Proposal { Kind = r.Kind, ProductId = r.ProductId, Quantity = r.Quantity, Total = r.Total, Source = (r.Source ?? "Reviewed receipt")[..Math.Min((r.Source ?? "Reviewed receipt").Length, 4000)], CreatedBy = Actor(c), RequestKey = r.RequestKey }; db.Proposals.Add(p); Audit(db, c, "proposal.created", p.Id); await db.SaveChangesAsync(); return Results.Ok(p);
}).RequireAuthorization();
app.MapPut("/api/proposals/{id:guid}", async (Guid id, EditProposal r, AppDb db, HttpContext c) =>
{
    var p = await db.Proposals.FindAsync(id); if (p is null) return Results.NotFound(); if (p.Status != "pending" || p.Version != r.Version) return Results.Conflict(new { error = "Reload the pending proposal." }); if (r.Quantity <= 0 || r.Quantity > 1000000 || r.Total < 0 || r.Total > 1000000000) return Results.BadRequest(); p.Quantity = r.Quantity; p.Total = r.Total; p.Version++; Audit(db, c, "proposal.edited", id); await db.SaveChangesAsync(); return Results.Ok(p);
}).RequireAuthorization();
app.MapPost("/api/proposals/{id:guid}/approve", async (Guid id, Approval r, AppDb db, WriteGate gate, HttpContext c) =>
{
    await gate.Lock.WaitAsync(); try
    {
        await using var tx = await db.Database.BeginTransactionAsync(System.Data.IsolationLevel.Serializable);
        var p = await db.Proposals.FindAsync(id); if (p is null) return Results.NotFound(); if (p.Status == "approved") return Results.Ok(new { alreadyApproved = true }); if (p.Status != "pending" || p.Version != r.Version) return Results.Conflict(new { error = "Proposal changed. Reload it." });
        if (p.Total is null || p.Total <= 0) return Results.BadRequest(new { error = p.Kind == "sale" ? "Enter the total selling price before approval. Profit cannot be inferred from purchase cost." : "Enter the purchase total before approval." });
        var product = await db.Products.SingleAsync(x => x.Id == p.ProductId); decimal cost = 0; string alert = "";
        if (p.Kind == "purchase")
        {
            decimal unit = p.Total.Value / p.Quantity; if (product.AverageCost > 0 && Math.Abs(unit - product.AverageCost) / product.AverageCost > 0.35m) alert = "Purchase unit cost differs by more than 35% from current weighted cost. Review supplier and pack size.";
            if (alert != "" && !r.AcknowledgeAnomaly) return Results.Conflict(new { error = alert, requiresAnomalyAcknowledgement = true });
            product.AverageCost = (product.Stock * product.AverageCost + p.Total.Value) / (product.Stock + p.Quantity); product.Stock += p.Quantity; cost = p.Total.Value;
        }
        else { if (product.Stock < p.Quantity) return Results.Conflict(new { error = "Insufficient approved stock. Approve the purchase first." }); cost = p.Quantity * product.AverageCost; product.Stock -= p.Quantity; }
        p.Status = "approved"; p.Version++; db.Ledger.Add(new Ledger { ProposalId = p.Id, ProductId = p.ProductId, Kind = p.Kind, Quantity = p.Quantity, Total = p.Total.Value, Cost = cost }); Audit(db, c, "proposal.approved", id); await db.SaveChangesAsync(); await tx.CommitAsync(); return Results.Ok(new { proposal = p, product, alert });
    }
    finally { gate.Lock.Release(); }
}).RequireAuthorization("owner");
app.MapPost("/api/proposals/{id:guid}/reject", async (Guid id, AppDb db, HttpContext c) => { var p = await db.Proposals.FindAsync(id); if (p is null) return Results.NotFound(); if (p.Status != "pending") return Results.Conflict(); p.Status = "rejected"; p.Version++; Audit(db, c, "proposal.rejected", id); await db.SaveChangesAsync(); return Results.Ok(p); }).RequireAuthorization("owner");
app.MapPost("/api/receipts/read", async (HttpRequest req, IHttpClientFactory f) =>
{
    var form = await req.ReadFormAsync(); var file = form.Files.FirstOrDefault(); if (file is null || file.Length > 8_000_000 || file.Length == 0) return Results.BadRequest(new { error = "Upload a PNG or JPEG under 8 MB." });
    using var body = new MultipartFormDataContent(); body.Add(new StreamContent(file.OpenReadStream()), "file", Path.GetFileName(file.FileName)); var response = await f.CreateClient("ai").PostAsync("/ocr", body); if (!response.IsSuccessStatusCode) return Results.BadRequest(new { error = "OCR could not read this image. Try a clear PNG/JPEG." }); return Results.Content(await response.Content.ReadAsStringAsync(), "application/json");
}).RequireAuthorization().DisableAntiforgery();
app.MapPost("/api/voice/transcribe", async (HttpRequest req, IHttpClientFactory f) => { var form = await req.ReadFormAsync(); var file = form.Files.FirstOrDefault(); if (file is null || file.Length > 10_000_000) return Results.BadRequest(); using var body = new MultipartFormDataContent(); body.Add(new StreamContent(file.OpenReadStream()), "file", Path.GetFileName(file.FileName)); var response = await f.CreateClient("ai").PostAsync("/transcribe", body); return Results.Content(await response.Content.ReadAsStringAsync(), "application/json", statusCode: (int)response.StatusCode); }).RequireAuthorization().DisableAntiforgery();
app.MapPost("/api/workflows/propose", async (WorkflowInput r, AppDb db, HttpContext c) =>
{
    if (string.IsNullOrWhiteSpace(r.Text) || r.Text.Length > 2000) return Results.BadRequest();
    if (!r.Text.Contains("return", StringComparison.OrdinalIgnoreCase) && !r.Text.Contains("مرتجع") && !r.Text.Contains("مرتجعات")) return Results.BadRequest(new { error = "This verified vertical slice supports returns workflows. Describe a returns department or مرتجعات." });
    var schema = new { fields = new[] { new { name = "saleId", type = "saleReference", required = true }, new { name = "quantity", type = "positiveNumber", required = true }, new { name = "reason", type = "text", required = true } }, approvalRole = "owner", effects = new[] { "validate remaining returnable quantity", "restock at original cost", "reverse sale revenue and cost" } };
    var w = new Workflow { Description = r.Text, SchemaJson = JsonSerializer.Serialize(schema) }; db.Workflows.Add(w); Audit(db, c, "workflow.proposed", w.Id); await db.SaveChangesAsync(); return Results.Ok(w);
}).RequireAuthorization();
app.MapPost("/api/workflows/{id:guid}/approve", async (Guid id, AppDb db, HttpContext c) => { var w = await db.Workflows.FindAsync(id); if (w is null) return Results.NotFound(); w.Status = "active"; Audit(db, c, "workflow.activated", id); await db.SaveChangesAsync(); return Results.Ok(w); }).RequireAuthorization("owner");
app.MapPost("/api/workflows/{id:guid}/records", async (Guid id, ReturnInput r, AppDb db, HttpContext c) =>
{
    var w = await db.Workflows.FindAsync(id); if (w?.Status != "active") return Results.BadRequest(new { error = "Activate the workflow first." }); var sale = await db.Ledger.FindAsync(r.SaleId); if (sale?.Kind != "sale" || r.Quantity <= 0 || r.Quantity > sale.Quantity || string.IsNullOrWhiteSpace(r.Reason) || r.Reason.Length > 500) return Results.BadRequest(new { error = "Choose a real sale, a valid quantity and a reason." });
    var record = new WorkflowRecord { WorkflowId = id, SaleId = r.SaleId, Quantity = r.Quantity, Reason = r.Reason }; db.WorkflowRecords.Add(record); Audit(db, c, "return.proposed", record.Id); await db.SaveChangesAsync(); return Results.Ok(record);
}).RequireAuthorization();
app.MapPost("/api/workflow-records/{id:guid}/approve", async (Guid id, AppDb db, WriteGate gate, HttpContext c) =>
{
    await gate.Lock.WaitAsync(); try { await using var tx = await db.Database.BeginTransactionAsync(System.Data.IsolationLevel.Serializable); var r = await db.WorkflowRecords.FindAsync(id); if (r is null) return Results.NotFound(); if (r.Status == "approved") return Results.Ok(new { alreadyApproved = true }); var sale = await db.Ledger.SingleAsync(x => x.Id == r.SaleId); var returns = await db.Ledger.Where(x => x.OriginalSaleId == sale.Id).ToListAsync(); if (returns.Sum(x => x.Quantity) + r.Quantity > sale.Quantity) return Results.Conflict(new { error = "Return exceeds the remaining sold quantity." }); var product = await db.Products.FindAsync(sale.ProductId); var cost = sale.Cost / sale.Quantity * r.Quantity; var amount = sale.Total / sale.Quantity * r.Quantity; product!.AverageCost = (product.Stock * product.AverageCost + cost) / (product.Stock + r.Quantity); product.Stock += r.Quantity; r.Status = "approved"; db.Ledger.Add(new Ledger { ProposalId = r.Id, OriginalSaleId = sale.Id, Kind = "return", ProductId = sale.ProductId, Quantity = r.Quantity, Total = amount, Cost = cost }); Audit(db, c, "return.approved", id); await db.SaveChangesAsync(); await tx.CommitAsync(); return Results.Ok(new { record = r, product, refund = amount }); } finally { gate.Lock.Release(); }
}).RequireAuthorization("owner");
app.MapPost("/api/documents", async (DocumentInput r, AppDb db, HttpContext c) => { if (string.IsNullOrWhiteSpace(r.Title) || r.Title.Length > 150 || string.IsNullOrWhiteSpace(r.Text) || r.Text.Length > 20000) return Results.BadRequest(); var d = new BusinessDocument { Title = r.Title, Text = r.Text }; db.Documents.Add(d); Audit(db, c, "document.added", d.Id); await db.SaveChangesAsync(); return Results.Ok(new { d.Id, d.Title }); }).RequireAuthorization("owner");
app.MapPost("/api/ask", async (Question r, AppDb db, IHttpClientFactory f) => { if (string.IsNullOrWhiteSpace(r.Text) || r.Text.Length > 2000) return Results.BadRequest(); return Results.Ok(await AI(f, "/ask", new { question = r.Text, documents = await db.Documents.Select(x => new { id = x.Id, title = x.Title, text = x.Text }).ToListAsync() })); }).RequireAuthorization();
app.MapGet("/api/forecast/{id}", async (string id, AppDb db, IHttpClientFactory f) =>
{
    var p = await db.Products.FindAsync(id); if (p is null) return Results.NotFound(); var sales = await db.Ledger.Where(x => x.ProductId == id && x.Kind == "sale").ToListAsync(); var since = DateTime.UtcNow.Date.AddDays(-55); var values = Enumerable.Range(0, 56).Select(i => new { date = since.AddDays(i).ToString("yyyy-MM-dd"), quantity = sales.Where(x => x.CreatedAt.Date == since.AddDays(i)).Sum(x => x.Quantity) }).ToList(); int days = sales.Select(x => x.CreatedAt.Date).Distinct().Count();
    if (days < 14) return Results.Ok(new { status = "insufficient_history", message = "At least 14 distinct sales days are required for a store-specific estimate. The benchmark panel uses historical US retail data, not this shop.", stock = p.Stock, leadDays = p.LeadDays, safetyStock = p.ReorderPoint, history = values });
    var result = await AI(f, "/forecast", new { history = values.Select(x => x.quantity), stock = p.Stock, leadDays = p.LeadDays, safetyStock = p.ReorderPoint }); return Results.Ok(result);
}).RequireAuthorization();
app.MapGet("/api/benchmarks", async (IHttpClientFactory f) => { var response = await f.CreateClient("ai").GetAsync("/benchmarks"); response.EnsureSuccessStatusCode(); return Results.Content(await response.Content.ReadAsStringAsync(), "application/json"); }).RequireAuthorization();
app.MapGet("/api/audit", async (AppDb db) => await db.Audits.OrderByDescending(x => x.Id).Take(100).ToListAsync()).RequireAuthorization("owner");
app.MapGet("/api/ops", async (OpsMonitor monitor, IHttpClientFactory f) => { var sw = System.Diagnostics.Stopwatch.StartNew(); bool healthy = false; try { using var timeout = new CancellationTokenSource(TimeSpan.FromSeconds(3)); var response = await f.CreateClient("ai").GetAsync("/health", timeout.Token); healthy = response.IsSuccessStatusCode; } catch { } return Results.Ok(new { api = "healthy", aiService = healthy ? "healthy" : "unavailable", aiProbeMs = sw.Elapsed.TotalMilliseconds, telemetry = monitor.Snapshot(), remediation = "Check service logs and restart the failed AI service if needed. No automatic business changes." }); }).RequireAuthorization("owner");
app.MapPost("/api/ops/simulate-failure", () => Results.Json(new { simulation = true, error = "Intentional AIOps demonstration failure. No records changed." }, statusCode: 503)).RequireAuthorization("owner");
app.MapFallbackToFile("index.html"); app.Run();
record Login(string Email, string Password); record Command(string Text, string RequestKey); record ManualProposal(string Kind, string ProductId, decimal Quantity, decimal? Total, string RequestKey, string? Source); record EditProposal(decimal Quantity, decimal? Total, int Version); record Approval(int Version, bool AcknowledgeAnomaly = false); record WorkflowInput(string Text); record ReturnInput(Guid SaleId, decimal Quantity, string Reason); record DocumentInput(string Title, string Text); record Question(string Text);
