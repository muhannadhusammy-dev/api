import React, { useState, useEffect, useRef } from "react";
import { createRoot } from "react-dom/client";
import {
  LayoutDashboard,
  MessageSquare,
  Receipt,
  Boxes,
  Workflow,
  BookOpen,
  Activity,
  BarChart3,
  ArrowUpRight,
  Check,
  Plus,
  Mic,
  Square,
  Upload,
  LogOut,
  ShieldCheck,
  ChevronRight,
  Search,
  AlertTriangle,
} from "lucide-react";
import "./style.css";
async function api(path: string, method = "GET", body?: any) {
  let headers: Record<string, string> = { "X-Tajer-Request": "1" };
  if (body && !(body instanceof FormData))
    headers["Content-Type"] = "application/json";
  let r = await fetch("/api/" + path, {
    method,
    headers,
    credentials: "include",
    body:
      body instanceof FormData ? body : body ? JSON.stringify(body) : undefined,
  });
  let d = await r.json().catch(() => ({}));
  if (!r.ok)
    throw Object.assign(Error(d.error || d.detail || "Request failed"), {
      status: r.status,
      data: d,
    });
  return d;
}
const money = (x: number) =>
  new Intl.NumberFormat("en-EG", {
    style: "currency",
    currency: "EGP",
    maximumFractionDigits: 0,
  }).format(x || 0);
const num = (x: number) =>
  Number(x || 0).toLocaleString("en", { maximumFractionDigits: 3 });
function App() {
  const [user, setUser] = useState<any>(null),
    [loading, setLoading] = useState(true),
    [ar, setAr] = useState(false),
    [tab, setTab] = useState("Overview"),
    [data, setData] = useState<any>(null),
    [notice, setNotice] = useState(""),
    [busy, setBusy] = useState(false),
    [command, setCommand] = useState(""),
    [reply, setReply] = useState("");
  const [receipt, setReceipt] = useState<any>(null),
    [line, setLine] = useState({
      productId: "oil",
      quantity: "50",
      total: "12000",
    }),
    [workflowText, setWorkflowText] = useState(
      "Create a returns department with owner approval",
    ),
    [question, setQuestion] = useState("ما هي سياسة المرتجعات؟"),
    [answer, setAnswer] = useState<any>(null),
    [bench, setBench] = useState<any>(null),
    [ops, setOps] = useState<any>(null),
    [forecast, setForecast] = useState<any>(null),
    [recording, setRecording] = useState(false),
    [docTitle, setDocTitle] = useState(""),
    [docText, setDocText] = useState("");
  const recorder = useRef<MediaRecorder | null>(null),
    chunks = useRef<Blob[]>([]);
  const t = (en: string, arabic: string) => (ar ? arabic : en);
  async function refresh() {
    setData(await api("dashboard"));
  }
  async function action(fn: () => Promise<any>, success?: string) {
    setBusy(true);
    setNotice("");
    try {
      await fn();
      if (success) setNotice(success);
      await refresh();
    } catch (e: any) {
      setNotice(e.message);
    } finally {
      setBusy(false);
    }
  }
  useEffect(() => {
    api("me")
      .then(async (u) => {
        setUser(u);
        await refresh();
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);
  useEffect(() => {
    if (!user) return;
    if (tab === "Evidence")
      api("benchmarks")
        .then(setBench)
        .catch((e) => setNotice(e.message));
    if (tab === "AIOps")
      api("ops")
        .then(setOps)
        .catch((e) => setNotice(e.message));
  }, [tab, user]);
  async function submitCommand() {
    await action(async () => {
      let r = await api("commands/propose", "POST", {
        text: command,
        requestKey: crypto.randomUUID(),
      });
      setReply(r.interpretation?.message || "Proposal already exists.");
    });
  }
  async function uploadReceipt(file: File) {
    let form = new FormData();
    form.append("file", file);
    await action(async () => {
      let r = await api("receipts/read", "POST", form);
      setReceipt(r);
      setLine({
        productId: r.productId || "oil",
        quantity: r.quantity?.toString() || "",
        total: r.total?.toString() || "",
      });
    });
  }
  async function audioFile(file: Blob, name = "recording.webm") {
    let form = new FormData();
    form.append("file", file, name);
    await action(async () => {
      let r = await api("voice/transcribe", "POST", form);
      setCommand(r.text);
      setReply(r.warning);
      setTab("Assistant");
    });
  }
  async function toggleRecord() {
    if (recording) {
      recorder.current?.stop();
      setRecording(false);
      return;
    }
    try {
      let stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      let rec = new MediaRecorder(stream);
      recorder.current = rec;
      chunks.current = [];
      rec.ondataavailable = (e) => chunks.current.push(e.data);
      rec.onstop = () => {
        stream.getTracks().forEach((x) => x.stop());
        audioFile(new Blob(chunks.current, { type: rec.mimeType }));
      };
      rec.start();
      setRecording(true);
      setTimeout(() => {
        if (rec.state === "recording") {
          rec.stop();
          setRecording(false);
        }
      }, 60000);
    } catch (e: any) {
      setNotice(
        "Microphone unavailable. Upload an audio file instead. " + e.message,
      );
    }
  }
  if (loading)
    return <div className="loading">TajerOS · Loading your workspace…</div>;
  if (!user)
    return (
      <div className="login">
        <div className="login-story">
          <span className="brand">
            تاجر<span>OS</span>
          </span>
          <p className="eyebrow">A LITTLE LESS ADMIN. A LOT MORE BUSINESS.</p>
          <h1>
            Your business.
            <br />
            In your own words.
          </h1>
          <p>
            من الفاتورة للمخزون، ومن السؤال للقرار.
            <br />
            كل تغيير بموافقتك.
          </p>
          <div className="login-note">
            <ShieldCheck /> Review first. Approve when ready.
          </div>
        </div>
        <form
          className="login-form"
          onSubmit={(e) => {
            e.preventDefault();
            let f = new FormData(e.currentTarget);
            action(async () => {
              let u = await api("login", "POST", {
                email: f.get("email"),
                password: f.get("password"),
              });
              setUser(u);
            });
          }}
        >
          <span className="pill">LOCAL DEMONSTRATION</span>
          <h2>Welcome to your shop</h2>
          <p>Sign in to the TajerOS demo workspace.</p>
          <label>
            Email
            <input
              name="email"
              type="email"
              defaultValue="owner@tajer.local"
              required
            />
          </label>
          <label>
            Password
            <input
              name="password"
              type="password"
              defaultValue="TajerDemo!2026"
              required
            />
          </label>
          <button disabled={busy}>
            Open workspace <ArrowUpRight size={18} />
          </button>
          {notice && <p className="error">{notice}</p>}
          <small>
            Demo account only. Change credentials before deployment.
          </small>
        </form>
      </div>
    );
  const navigation = [
    ["Overview", "نظرة عامة", LayoutDashboard],
    ["Assistant", "المساعد", MessageSquare],
    ["Receipts", "الفواتير", Receipt],
    ["Inventory", "المخزون", Boxes],
    ["Workflows", "سير العمل", Workflow],
    ["Knowledge", "المعرفة", BookOpen],
    ["AIOps", "صحة النظام", Activity],
    ["Evidence", "نتائج النماذج", BarChart3],
  ] as const;
  const pending =
    data?.proposals?.filter((p: any) => p.status === "pending") || [];
  return (
    <div className={"app " + (ar ? "rtl" : "")} dir={ar ? "rtl" : "ltr"}>
      <aside>
        <a className="brand" href="#" onClick={() => setTab("Overview")}>
          تاجر<span>OS</span>
          <b>AI</b>
        </a>
        <div className="shop">
          <span className="shop-icon">N</span>
          <div>
            <strong>Nile Market</strong>
            <small>{t("Demo grocery workspace", "مساحة بقالة تجريبية")}</small>
          </div>
        </div>
        <p className="nav-label">{t("YOUR WORKSPACE", "مساحة العمل")}</p>
        <nav>
          {navigation.map(([id, label, Icon]) => (
            <button
              key={id}
              className={tab === id ? "active" : ""}
              onClick={() => setTab(id)}
            >
              <Icon size={18} />
              {ar ? label : id}
              {id === "Assistant" && pending.length > 0 && (
                <em>{pending.length}</em>
              )}
            </button>
          ))}
        </nav>
        <div className="aside-bottom">
          <ShieldCheck size={18} />
          <span>
            {t("You stay in control", "القرار دايمًا بإيدك")}
            <small>
              {t("Approval before every change", "موافقة قبل أي تغيير")}
            </small>
          </span>
        </div>
      </aside>
      <main>
        <header>
          <div className="breadcrumb">
            Nile Market <ChevronRight size={14} />{" "}
            {ar ? navigation.find((n) => n[0] === tab)?.[1] : tab}
          </div>
          <div className="header-actions">
            <button className="ghost" onClick={() => setAr(!ar)}>
              {ar ? "English" : "العربية"}
            </button>
            <span className="avatar">NM</span>
            <button
              title="Sign out"
              className="icon-button"
              onClick={() =>
                action(async () => {
                  await api("logout", "POST");
                  setUser(null);
                })
              }
            >
              <LogOut size={17} />
            </button>
          </div>
        </header>
        {notice && (
          <div role="status" className="notice">
            <AlertTriangle size={17} />
            {notice}
            <button onClick={() => setNotice("")}>×</button>
          </div>
        )}
        {busy && <div className="busy-line" />}
        {tab === "Overview" && data && (
          <>
            <section className="welcome">
              <div>
                <p className="eyebrow">
                  {t("YOUR SHOP, WORKING SMARTER", "محلك… بإدارة أذكى")}
                </p>
                <h1>
                  {t("Less paperwork.", "ورق أقل.")}
                  <br />
                  <span>{t("More room to grow.", "وقت أكتر لشغلك.")}</span>
                </h1>
                <p>
                  {t(
                    "Tell TajerOS what happened. Review the details. Keep your business moving.",
                    "قول لتاجر إيه اللي حصل، راجع التفاصيل، وكمّل شغلك.",
                  )}
                </p>
                <button onClick={() => setTab("Assistant")}>
                  {t("Talk to your business", "اتكلم مع مساعدك")}{" "}
                  <ArrowUpRight size={18} />
                </button>
              </div>
              <div className="voice-card">
                <span className="mini-tag">
                  {t("TRY IT IN EGYPTIAN ARABIC", "جرّبها بالمصري")}
                </span>
                <p dir="rtl">
                  «اشتريت 50 كرتونة زيت بـ 12 ألف جنيه، وبعت 15 كرتونة»
                </p>
                <div className="wave">▂ ▅ ▃ ▇ ▄ ▂ ▆ ▃ ▅ ▂ ▆ ▄ ▇ ▃ ▂</div>
                <small>
                  {t(
                    "A proposal first. Your approval next.",
                    "اقتراح الأول. وموافقتك بعده.",
                  )}
                </small>
              </div>
            </section>
            <div className="stats">
              {[
                [
                  t("Sales revenue", "إيراد المبيعات"),
                  money(data.revenue),
                  "Approved sales less returns",
                ],
                [
                  t("Gross profit", "مجمل الربح"),
                  money(data.grossProfit),
                  "Before expenses and tax",
                ],
                [
                  t("Inventory value", "قيمة المخزون"),
                  money(data.inventoryValue),
                  "Weighted average cost",
                ],
                [
                  t("Awaiting approval", "بانتظار الموافقة"),
                  pending.length,
                  "No records changed yet",
                ],
              ].map(([title, value, note]) => (
                <div className="stat" key={String(title)}>
                  <span>{title}</span>
                  <strong>{value}</strong>
                  <small>{note}</small>
                </div>
              ))}
            </div>
            <section className="two-col">
              <div className="panel">
                <div className="panel-title">
                  <h2>{t("Your next steps", "خطوتك الجاية")}</h2>
                  <span className="pill">{pending.length} pending</span>
                </div>
                <div className="step" onClick={() => setTab("Receipts")}>
                  <span>01</span>
                  <div>
                    <strong>
                      {t(
                        "Turn a receipt into a reviewed purchase",
                        "حوّل الفاتورة لمشتريات قابلة للمراجعة",
                      )}
                    </strong>
                    <p>Upload → check fields → propose → approve</p>
                  </div>
                  <ArrowUpRight />
                </div>
                <div className="step" onClick={() => setTab("Workflows")}>
                  <span>02</span>
                  <div>
                    <strong>
                      {t("Create a returns department", "أنشئ قسم مرتجعات")}
                    </strong>
                    <p>Generate a form and an owner approval process</p>
                  </div>
                  <ArrowUpRight />
                </div>
              </div>
              <div className="panel">
                <h2>{t("Stock to watch", "تابع مخزونك")}</h2>
                {data.products.map((p: any) => (
                  <div className="stock-row" key={p.id}>
                    <span className="product-icon">
                      <Boxes size={19} />
                    </span>
                    <div>
                      <strong>{ar ? p.arabicName : p.name}</strong>
                      <small>
                        {p.unit} · {money(p.averageCost)} cost
                      </small>
                    </div>
                    <b className={p.stock <= p.reorderPoint ? "low" : ""}>
                      {num(p.stock)}
                      <small>in stock</small>
                    </b>
                  </div>
                ))}
              </div>
            </section>
          </>
        )}
        {tab === "Assistant" && (
          <section>
            <Title
              eyebrow="EGYPTIAN ARABIC ASSISTANT"
              title={t(
                "Say it. Review it. Approve it.",
                "قولها. راجعها. وافق عليها.",
              )}
              text={t(
                "Text and voice become proposed actions. Nothing posts automatically.",
                "النص والصوت بيتحولوا لاقتراحات. مفيش ترحيل تلقائي.",
              )}
            />
            <div className="panel">
              <textarea
                id="command"
                rows={4}
                value={command}
                onChange={(e) => setCommand(e.target.value)}
                placeholder="أنا اشتريت 50 كرتونة زيت بـ 12 ألف جنيه، وبعت 15 كرتونة. قولي كسبت كام"
                dir="auto"
              />
              <div className="toolbar">
                <button disabled={busy || !command} onClick={submitCommand}>
                  {t("Prepare proposal", "حضّر الاقتراح")}{" "}
                  <ArrowUpRight size={17} />
                </button>
                <button className="secondary" onClick={toggleRecord}>
                  {recording ? <Square size={17} /> : <Mic size={17} />}{" "}
                  {recording ? "Stop recording" : t("Record voice", "سجّل صوت")}
                </button>
                <label className="file-button">
                  {t("Upload audio", "ارفع تسجيل")}
                  <input
                    type="file"
                    accept="audio/*"
                    onChange={(e) =>
                      e.target.files?.[0] &&
                      audioFile(e.target.files[0], e.target.files[0].name)
                    }
                  />
                </label>
              </div>
              <div className="chips">
                <button
                  onClick={() =>
                    setCommand(
                      "أنا اشتريت 50 كرتونة زيت بـ 12 ألف جنيه، وبعت 15 كرتونة. قولي كسبت كام وإمتى لازم أطلب بضاعة تاني.",
                    )
                  }
                >
                  Oil purchase + sale
                </button>
                <button
                  onClick={() => setCommand("اشتريت 5 كرتونة زيت ب 5000 جنيه")}
                >
                  Try unusual purchase cost
                </button>
              </div>
              {reply && (
                <div className="assistant-reply">
                  <ShieldCheck size={20} />
                  <p>{reply}</p>
                </div>
              )}
            </div>
            <h2>{t("Proposals to review", "اقتراحات للمراجعة")}</h2>
            <div className="proposal-list">
              {pending.length ? (
                pending.map((p: any) => (
                  <ProposalCard
                    key={p.id + ":" + p.version}
                    proposal={p}
                    data={data}
                    busy={busy}
                    action={action}
                  />
                ))
              ) : (
                <Empty text="No pending proposals. Describe a transaction to begin." />
              )}
            </div>
          </section>
        )}
        {tab === "Receipts" && (
          <section>
            <Title
              eyebrow="DOCUMENT INTELLIGENCE"
              title={t("From paper to a proposal.", "من الورق لاقتراح واضح.")}
              text="Arabic and English OCR. Check every extracted field before creating a purchase."
            />
            <div className="two-col">
              <div className="panel">
                <label className="dropzone">
                  <Upload size={38} />
                  <strong>Upload a receipt image</strong>
                  <span>PNG or JPEG · up to 8 MB</span>
                  <input
                    id="receipt-file"
                    type="file"
                    accept="image/png,image/jpeg"
                    onChange={(e) =>
                      e.target.files?.[0] && uploadReceipt(e.target.files[0])
                    }
                  />
                </label>
                <p className="small">
                  Use data/demo_receipt.png from the project for the guided
                  demonstration. It is a synthetic receipt fixture.
                </p>
                {receipt && (
                  <>
                    <h3>OCR transcript</h3>
                    <pre dir="auto">{receipt.text}</pre>
                    <p className="small">{receipt.warning}</p>
                  </>
                )}
              </div>
              <div className="panel">
                <h2>Review purchase details</h2>
                <label>
                  Product
                  <select
                    value={line.productId}
                    onChange={(e) =>
                      setLine({ ...line, productId: e.target.value })
                    }
                  >
                    {data?.products.map((p: any) => (
                      <option key={p.id} value={p.id}>
                        {p.name} / {p.arabicName}
                      </option>
                    ))}
                  </select>
                </label>
                <label>
                  Quantity (cartons)
                  <input
                    type="number"
                    min="0.01"
                    step="any"
                    value={line.quantity}
                    onChange={(e) =>
                      setLine({ ...line, quantity: e.target.value })
                    }
                  />
                </label>
                <label>
                  Total purchase cost (EGP)
                  <input
                    type="number"
                    min="0.01"
                    step="any"
                    value={line.total}
                    onChange={(e) =>
                      setLine({ ...line, total: e.target.value })
                    }
                  />
                </label>
                {receipt && (
                  <div className="details">
                    <span>Supplier: {receipt.supplier || "Not detected"}</span>
                    <span>Date: {receipt.date || "Not detected"}</span>
                  </div>
                )}
                <button
                  disabled={busy || !receipt || !line.quantity || !line.total}
                  onClick={() =>
                    action(async () => {
                      await api("proposals", "POST", {
                        kind: "purchase",
                        ...line,
                        quantity: Number(line.quantity),
                        total: Number(line.total),
                        source: receipt.text,
                        requestKey: crypto.randomUUID(),
                      });
                      setTab("Assistant");
                    }, "Purchase proposed. Review and approve it to update stock.")
                  }
                >
                  Create purchase proposal <Plus size={17} />
                </button>
                <p className="small">
                  One reviewed product line per proposal. Supplier and date are
                  extraction evidence, not a tax invoice submission.
                </p>
              </div>
            </div>
          </section>
        )}
        {tab === "Inventory" && data && (
          <section>
            <Title
              eyebrow="STOCK & FINANCIAL CONTROL"
              title={t("Know what is on your shelves.", "اعرف اللي على رفوفك.")}
              text="Approved purchases, sales and returns determine stock and weighted average cost."
            />
            <div className="panel table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Product</th>
                    <th>Stock</th>
                    <th>Average unit cost</th>
                    <th>Value</th>
                    <th>Reorder point</th>
                    <th />
                  </tr>
                </thead>
                <tbody>
                  {data.products.map((p: any) => (
                    <tr key={p.id}>
                      <td>
                        <strong>{p.name}</strong>
                        <small>{p.arabicName}</small>
                      </td>
                      <td>
                        {num(p.stock)} {p.unit}
                      </td>
                      <td>{money(p.averageCost)}</td>
                      <td>{money(p.stock * p.averageCost)}</td>
                      <td>{p.reorderPoint}</td>
                      <td>
                        <button
                          className="secondary"
                          onClick={() =>
                            action(async () =>
                              setForecast(await api("forecast/" + p.id)),
                            )
                          }
                        >
                          Stock outlook
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            {forecast && (
              <div className="panel">
                <h2>Stock outlook</h2>
                <p>{forecast.message || forecast.note}</p>
                {forecast.status === "estimate" && (
                  <>
                    <p>
                      Daily estimate: {num(forecast.dailyRate)} · Cover:{" "}
                      {forecast.stockCoverDays
                        ? num(forecast.stockCoverDays) + " days"
                        : "not estimable"}{" "}
                      ·{" "}
                      {forecast.reorderNow
                        ? "Reorder now"
                        : "Above reorder point"}
                    </p>
                    <LineChart
                      actual={forecast.next7}
                      labels={["1", "2", "3", "4", "5", "6", "7"]}
                    />
                  </>
                )}
              </div>
            )}
            <h2>Approved transaction ledger</h2>
            <div className="panel table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Type</th>
                    <th>Product</th>
                    <th>Quantity</th>
                    <th>Total</th>
                    <th>Cost</th>
                    <th>Reference</th>
                  </tr>
                </thead>
                <tbody>
                  {data.ledger.map((x: any) => (
                    <tr key={x.id}>
                      <td>
                        <span className="pill">{x.kind}</span>
                      </td>
                      <td>{x.productId}</td>
                      <td>{num(x.quantity)}</td>
                      <td>{money(x.total)}</td>
                      <td>{money(x.cost)}</td>
                      <td className="small">{x.id.slice(0, 8)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {!data.ledger.length && (
                <Empty text="No posted transactions yet." />
              )}
            </div>
          </section>
        )}
        {tab === "Workflows" && data && (
          <section>
            <Title
              eyebrow="SELF-CONFIGURING WORKFLOWS"
              title={t("A process that fits your shop.", "إجراء مناسب لشغلك.")}
              text="This verified prototype generates a returns form and connects approval to stock and sales reversals."
            />
            <div className="panel">
              <label>
                Describe the department or process
                <textarea
                  value={workflowText}
                  onChange={(e) => setWorkflowText(e.target.value)}
                  rows={2}
                />
              </label>
              <button
                disabled={busy}
                onClick={() =>
                  action(
                    () =>
                      api("workflows/propose", "POST", { text: workflowText }),
                    "Workflow proposed. Review its fields and effects before activation.",
                  )
                }
              >
                Generate proposed workflow <Workflow size={18} />
              </button>
              <p className="small">
                Supported: returns / مرتجعات. Arbitrary code, database tables
                and unrestricted workflows are not generated.
              </p>
            </div>
            {data.workflows.map((w: any) => (
              <div className="panel" key={w.id}>
                <div className="panel-title">
                  <h2>{w.name}</h2>
                  <span className="pill">{w.status}</span>
                </div>
                <p>{w.description}</p>
                <div className="schema">
                  {JSON.parse(w.schemaJson).fields.map((f: any) => (
                    <span key={f.name}>
                      {f.name}
                      <small>{f.type} · required</small>
                    </span>
                  ))}
                </div>
                <p className="small">
                  Owner approval → validate sale quantity → restock at
                  historical cost → reverse revenue and COGS
                </p>
                {w.status === "pending" ? (
                  <button
                    disabled={busy}
                    onClick={() =>
                      action(
                        () => api("workflows/" + w.id + "/approve", "POST"),
                        "Returns workflow activated.",
                      )
                    }
                  >
                    Approve workflow
                  </button>
                ) : (
                  <DynamicReturnForm
                    workflow={w}
                    sales={data.ledger.filter((x: any) => x.kind === "sale")}
                    action={action}
                    busy={busy}
                  />
                )}
              </div>
            ))}
            {data.workflowRecords.map((r: any) => (
              <div className="panel compact" key={r.id}>
                <div>
                  <strong>Return {num(r.quantity)} carton(s)</strong>
                  <p>
                    {r.reason} · {r.status}
                  </p>
                </div>
                {r.status === "pending" && (
                  <button
                    disabled={busy}
                    onClick={() =>
                      action(
                        () =>
                          api("workflow-records/" + r.id + "/approve", "POST"),
                        "Return approved: stock and financial reversals posted.",
                      )
                    }
                  >
                    Approve return
                  </button>
                )}
              </div>
            ))}
          </section>
        )}
        {tab === "Knowledge" && (
          <section>
            <Title
              eyebrow="YOUR DOCUMENTS, WITH SOURCES"
              title={t("Answers you can trace.", "إجابات تقدر تراجع مصدرها.")}
              text="Company policies stay separate from business transactions. No unsupported regulatory advice."
            />
            <div className="two-col">
              <div className="panel">
                <label>
                  Ask about an approved document
                  <textarea
                    rows={3}
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                    dir="auto"
                  />
                </label>
                <button
                  disabled={busy}
                  onClick={() =>
                    action(async () =>
                      setAnswer(await api("ask", "POST", { text: question })),
                    )
                  }
                >
                  Find supporting evidence <Search size={17} />
                </button>
                {answer && (
                  <div className="answer">
                    <span className="pill">{answer.mode}</span>
                    <p className="answer-text" dir="auto">
                      {answer.answer}
                    </p>
                    {answer.citations.map((c: any) => (
                      <details key={c.id}>
                        <summary>
                          [{c.number}] {c.title}
                        </summary>
                        <p dir="auto">{c.text}</p>
                        <small>Document {c.documentId}</small>
                      </details>
                    ))}
                  </div>
                )}
              </div>
              <div className="panel">
                <h2>Approved knowledge</h2>
                {data?.documents.map((d: any) => (
                  <div className="doc" key={d.id}>
                    <BookOpen size={19} />
                    <div>
                      <strong>{d.title}</strong>
                      <small>{d.source}</small>
                    </div>
                  </div>
                ))}
                <h3>Add a company policy</h3>
                <label>
                  Title
                  <input
                    value={docTitle}
                    onChange={(e) => setDocTitle(e.target.value)}
                  />
                </label>
                <label>
                  Policy text
                  <textarea
                    rows={4}
                    value={docText}
                    onChange={(e) => setDocText(e.target.value)}
                  />
                </label>
                <button
                  className="secondary"
                  disabled={busy || !docTitle || !docText}
                  onClick={() =>
                    action(async () => {
                      await api("documents", "POST", {
                        title: docTitle,
                        text: docText,
                      });
                      setDocTitle("");
                      setDocText("");
                    }, "Company policy added.")
                  }
                >
                  Add approved document
                </button>
              </div>
            </div>
          </section>
        )}
        {tab === "AIOps" && (
          <section>
            <Title
              eyebrow="AIOPS / OPERATIONAL HEALTH"
              title={t(
                "Keep the assistant dependable.",
                "خلي مساعدك جاهز للشغل.",
              )}
              text="Observe API errors, request latency and AI-service availability. Demonstration incidents are labelled and isolated."
            />
            <div className="toolbar">
              <button
                onClick={() => action(async () => setOps(await api("ops")))}
              >
                Refresh health
              </button>
              <button
                className="secondary"
                onClick={() =>
                  action(async () => {
                    try {
                      await api("ops/simulate-failure", "POST");
                    } catch (e: any) {
                      if (e.status !== 503) throw e;
                    }
                    setOps(await api("ops"));
                  }, "Simulated 503 detected. No business records changed.")
                }
              >
                Simulate a safe failure
              </button>
            </div>
            {ops && (
              <>
                <div className="stats">
                  <div className="stat">
                    <span>Business API</span>
                    <strong>{ops.api}</strong>
                    <small>Current process</small>
                  </div>
                  <div className="stat">
                    <span>AI service</span>
                    <strong>{ops.aiService}</strong>
                    <small>Probe {num(ops.aiProbeMs)} ms</small>
                  </div>
                  <div className="stat">
                    <span>Real error rate</span>
                    <strong>{num(ops.telemetry.errorRatePercent)}%</strong>
                    <small>Last 5 minutes</small>
                  </div>
                  <div className="stat">
                    <span>Request p95</span>
                    <strong>{num(ops.telemetry.p95Milliseconds)} ms</strong>
                    <small>{ops.telemetry.totalRequests} real requests</small>
                  </div>
                </div>
                {ops.aiService !== "healthy" && (
                  <div className="notice">
                    AI service unavailable. Start or restart it; proposals
                    cannot silently change business records.
                  </div>
                )}
                {ops.telemetry.alerts.map((a: any) => (
                  <div className="notice" key={a.code}>
                    <AlertTriangle />
                    <div>
                      <strong>{a.code}</strong>
                      <p>{a.message}</p>
                    </div>
                  </div>
                ))}
                <p className="small">{ops.telemetry.policy}</p>
                <div className="panel table-wrap">
                  <table>
                    <thead>
                      <tr>
                        <th>Time</th>
                        <th>Route</th>
                        <th>Status</th>
                        <th>Latency</th>
                        <th>Origin</th>
                      </tr>
                    </thead>
                    <tbody>
                      {ops.telemetry.requests.map((r: any, i: number) => (
                        <tr key={i}>
                          <td>{new Date(r.at).toLocaleTimeString()}</td>
                          <td>{r.route}</td>
                          <td>{r.status}</td>
                          <td>{num(r.milliseconds)} ms</td>
                          <td>{r.simulated ? "SIMULATION" : "Live request"}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                <p className="small">{ops.remediation}</p>
              </>
            )}
          </section>
        )}
        {tab === "Evidence" && (
          <section>
            <Title
              eyebrow="MEASURED MODEL COMPARISONS"
              title="Evidence before claims."
              text="Benchmark results are kept separate from this shop’s financial records. Dataset and evaluation limits accompany every result."
            />
            {bench ? (
              Object.entries(bench)
                .filter(([k, v]: any) => v?.comparison)
                .map(([k, v]: any) => (
                  <div className="panel" key={k}>
                    <div className="panel-title">
                      <h2>{k.toUpperCase()}</h2>
                      <span className="pill">
                        {v.selected || "No defensible winner"}
                      </span>
                    </div>
                    <p>{v.data}</p>
                    <div className="table-wrap">
                      <table>
                        <thead>
                          <tr>
                            {Object.keys(v.comparison[0]).map((x) => (
                              <th key={x}>{x}</th>
                            ))}
                          </tr>
                        </thead>
                        <tbody>
                          {v.comparison.map((row: any, i: number) => (
                            <tr key={i}>
                              {Object.values(row).map((x: any, j: number) => (
                                <td key={j}>
                                  {typeof x === "number" ? num(x) : String(x)}
                                </td>
                              ))}
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                    {k === "forecast" && (
                      <>
                        <LineChart
                          actual={v.series.map((x: any) => x.Weekly_Sales)}
                          predicted={v.series.map((x: any) => x.prediction)}
                          labels={v.series.map((x: any) => x.Date)}
                        />
                        <p className="small">
                          US weekly aggregate sales (USD). Actual vs one-step
                          predictions, not an Egyptian demand forecast.
                        </p>
                      </>
                    )}
                    <p className="small">{v.limitations}</p>
                  </div>
                ))
            ) : (
              <Empty text="Loading measured results…" />
            )}
          </section>
        )}
        <footer>
          TajerOS AI ·{" "}
          {t(
            "Research prototype. Every business change needs approval.",
            "نموذج بحثي. كل تغيير في سجلات النشاط يحتاج موافقة.",
          )}
        </footer>
      </main>
    </div>
  );
}
function Title({ eyebrow, title, text }: any) {
  return (
    <div className="page-title">
      <p className="eyebrow">{eyebrow}</p>
      <h1>{title}</h1>
      <p>{text}</p>
    </div>
  );
}
function Empty({ text }: any) {
  return (
    <div className="empty">
      <Boxes size={30} />
      <p>{text}</p>
    </div>
  );
}
function ProposalCard({ proposal: p, data, busy, action }: any) {
  const [qty, setQty] = useState(String(p.quantity)),
    [total, setTotal] = useState(p.total == null ? "" : String(p.total)),
    [ack, setAck] = useState(false);
  let changed =
    Number(qty) !== p.quantity ||
    (total === "" ? null : Number(total)) !== p.total;
  let product = data.products.find((x: any) => x.id === p.productId);
  let abnormal =
    p.kind === "purchase" &&
    product?.averageCost > 0 &&
    Number(total) > 0 &&
    Math.abs(Number(total) / Number(qty) - product.averageCost) /
      product.averageCost >
      0.35;
  return (
    <div className="panel proposal">
      <div className="panel-title">
        <h3>
          {p.kind === "purchase" ? "Purchase" : "Sale"} · {product?.name}
        </h3>
        <span className="pill">Pending approval</span>
      </div>
      <div className="two-fields">
        <label>
          Quantity
          <input
            type="number"
            value={qty}
            onChange={(e) => setQty(e.target.value)}
          />
        </label>
        <label>
          {p.kind === "sale"
            ? "Total selling revenue (EGP)"
            : "Purchase total (EGP)"}
          <input
            type="number"
            value={total}
            placeholder="Required before approval"
            onChange={(e) => setTotal(e.target.value)}
          />
        </label>
      </div>
      {!total && (
        <p className="warning">
          Selling price is missing. Profit cannot be calculated from cost alone.
        </p>
      )}
      {p.warnings && <p className="small">{p.warnings}</p>}
      {abnormal && (
        <label className="check warning">
          <input
            type="checkbox"
            checked={ack}
            onChange={(e) => setAck(e.target.checked)}
          />{" "}
          Unit cost differs by over 35%. I reviewed the supplier price and pack
          size.
        </label>
      )}
      <div className="toolbar">
        {changed ? (
          <button
            disabled={busy}
            onClick={() =>
              action(
                () =>
                  api("proposals/" + p.id, "PUT", {
                    quantity: Number(qty),
                    total: total === "" ? null : Number(total),
                    version: p.version,
                  }),
                "Proposal updated. Review it before approval.",
              )
            }
          >
            Save reviewed fields
          </button>
        ) : (
          <button
            disabled={busy || !total || (abnormal && !ack)}
            onClick={() =>
              action(
                () =>
                  api("proposals/" + p.id + "/approve", "POST", {
                    version: p.version,
                    acknowledgeAnomaly: ack,
                  }),
                "Transaction approved and posted once.",
              )
            }
          >
            <Check size={17} />
            Approve {p.kind}
          </button>
        )}
        <button
          className="ghost"
          disabled={busy}
          onClick={() =>
            action(
              () => api("proposals/" + p.id + "/reject", "POST"),
              "Proposal rejected.",
            )
          }
        >
          Reject
        </button>
      </div>
    </div>
  );
}
function DynamicReturnForm({ workflow: w, sales, action, busy }: any) {
  let schema = JSON.parse(w.schemaJson);
  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        let f = new FormData(e.currentTarget);
        action(
          () =>
            api("workflows/" + w.id + "/records", "POST", {
              saleId: f.get("saleId"),
              quantity: Number(f.get("quantity")),
              reason: f.get("reason"),
            }),
          "Return submitted for owner approval.",
        );
      }}
    >
      <h3>Generated returns form</h3>
      <div className="three-fields">
        {schema.fields.map((f: any) => (
          <label key={f.name}>
            {f.name}
            {f.type === "saleReference" ? (
              <select name={f.name} required>
                <option value="">Select original sale</option>
                {sales.map((s: any) => (
                  <option key={s.id} value={s.id}>
                    {s.productId} · {s.quantity} sold · {s.id.slice(0, 8)}
                  </option>
                ))}
              </select>
            ) : (
              <input
                name={f.name}
                type={f.type === "positiveNumber" ? "number" : "text"}
                min={f.type === "positiveNumber" ? "0.01" : undefined}
                step="any"
                required={f.required}
              />
            )}
          </label>
        ))}
      </div>
      <button className="secondary" disabled={busy || !sales.length}>
        Submit return for approval
      </button>
      {!sales.length && (
        <p className="small">Approve a sale before creating a return.</p>
      )}
    </form>
  );
}
function LineChart({ actual, predicted, labels }: any) {
  let all = [...actual, ...(predicted || [])],
    max = Math.max(...all, 1),
    min = Math.min(...all, 0),
    h = 180,
    w = 800;
  let points = (arr: number[]) =>
    arr
      .map(
        (v, i) =>
          `${35 + (i * (w - 70)) / Math.max(arr.length - 1, 1)},${h - 25 - ((v - min) / (max - min)) * (h - 50)}`,
      )
      .join(" ");
  return (
    <div className="chart">
      <svg
        viewBox={`0 0 ${w} ${h}`}
        role="img"
        aria-label="Actual and predicted values"
      >
        <line x1="35" y1={h - 25} x2={w - 35} y2={h - 25} stroke="#dce2dd" />
        <polyline
          points={points(actual)}
          fill="none"
          stroke="#254d41"
          strokeWidth="3"
        />
        {predicted && (
          <polyline
            points={points(predicted)}
            fill="none"
            stroke="#b88b52"
            strokeWidth="3"
            strokeDasharray="7 4"
          />
        )}
      </svg>
      <div className="chart-labels">
        <span>{labels?.[0]}</span>
        <span>Actual {predicted ? "— — Predicted" : ""}</span>
        <span>{labels?.[labels.length - 1]}</span>
      </div>
    </div>
  );
}
createRoot(document.getElementById("root")!).render(<App />);
