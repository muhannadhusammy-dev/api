using System.Collections.Concurrent;
namespace TajerOS;

public sealed record RequestMetric(DateTime At, string Route, int Status, double Milliseconds, bool Simulated);
public sealed class OpsMonitor
{
    readonly ConcurrentQueue<RequestMetric> samples = new();
    public void Record(string route, int status, double ms) { samples.Enqueue(new(DateTime.UtcNow, route, status, ms, route.Contains("simulate-failure"))); while (samples.Count > 500) samples.TryDequeue(out _); }
    public object Snapshot()
    {
        var all = samples.ToArray(); var recent = all.Where(x => x.At > DateTime.UtcNow.AddMinutes(-5)).ToArray(); var real = recent.Where(x => !x.Simulated).ToArray(); var durations = real.Select(x => x.Milliseconds).Order().ToArray(); double p95 = durations.Length == 0 ? 0 : durations[(int)Math.Floor((durations.Length - 1) * .95)]; double errors = real.Length == 0 ? 0 : 100.0 * real.Count(x => x.Status >= 500) / real.Length; var alerts = new List<object>();
        if (real.Length >= 10 && errors > 5) alerts.Add(new { severity = "high", code = "API_ERROR_RATE", message = $"Real API error rate {errors:F1}% exceeds the demo 5% threshold.", simulation = false });
        if (durations.Length >= 10 && p95 > 3000) alerts.Add(new { severity = "warning", code = "SLOW_REQUESTS", message = $"API p95 {p95:F0} ms exceeds 3000 ms.", simulation = false });
        if (recent.Any(x => x.Simulated)) alerts.Add(new { severity = "demo", code = "SIMULATED_FAILURE", message = "A labelled demonstration request returned 503. Business records were not changed.", simulation = true });
        return new { windowMinutes = 5, totalRequests = real.Length, errorRatePercent = errors, p95Milliseconds = p95, alerts, requests = all.TakeLast(50).Reverse(), policy = "Fixed demonstration thresholds; no claim of trained production anomaly detection. Simulations are excluded from real error-rate and latency metrics." };
    }
}
