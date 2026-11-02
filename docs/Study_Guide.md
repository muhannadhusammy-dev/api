# TajerOS AI: project, business and technical study guide

## 1. Explain the project in one minute
TajerOS helps an Egyptian shop owner turn everyday descriptions and receipt images into business actions. The owner can describe a purchase in Egyptian Arabic, inspect the extracted quantity and price, then approve an inventory update. The application records sales, calculates gross profit, handles a generated returns form, answers questions from approved policies and monitors its own service health.

The long-term vision is an ERP that adapts to the business. The implemented submission demonstrates a controlled part of that vision: three products, one shop and a returns workflow template. It cannot invent an arbitrary department's accounting rules. A model can suggest an action, but C# validates and posts the financial effect. This distinction is essential to explain during your defense.

Egyptian explanation: «تاجر هو مساعد لصاحب المحل. تقول له اشتريت إيه أو ترفع الفاتورة، وهو يجهز اقتراح. أنت تراجع وتوافق، وبعدها المخزون والحسابات يتحدثوا. ولو البيانات ناقصة، زي سعر البيع، النظام ما يخمنش الربح.»

## 2. Customer and business value
Start with a small grocery or household-goods retailer that buys cartons and sells a known set of products. The buyer is the owner. A clerk enters receipts and sales. The owner approves changes and checks stock and profit. This narrow audience gives a clearer demonstration than simultaneously promising pharmacy safety, factory planning and restaurant production.

The pain is repeated manual entry, inconsistent product names, uncertainty about inventory and time spent finding policies. TajerOS proposes a simpler input method and makes the approval trail visible. These are product hypotheses. We have not interviewed merchants, measured adoption, or established willingness to pay. A polished demonstration is evidence of implementation, not proof of product-market fit.

Visa's 28 July 2025 release reports that 77% of surveyed Egyptian SMEs regard digital payments as important for growth and 53% adopted them in the preceding two years. These are survey findings about payments. They support exploring digitization, but do not measure demand for this product. Source: https://www.visa.com/en-eg/newsroom/egypt-smes-digital-payments-growth-study

| Route | Who pays whom | Fit for TajerOS | Decision and reason |
|---|---|---|---|
| B2B | Shop pays software provider | Owner controls records and approvals | Initial route; one accountable buyer |
| B2B2C | Platform serves merchant, merchant serves consumer | Supplier links and customer receipts may extend value | Expansion after basic shop reliability |
| B2C | Consumer pays software provider | Consumers do not run the shop's inventory | Weak initial fit |
| B2G | Government agency buys software | Possible SME digitization programme | Later procurement and integration work |
| G2B | Government provides service to businesses | Describes an agency's service model | Requires a government operator, not a label for ordinary SaaS |
| G2C | Government provides service to citizens | Distant from the first grocery workflow | Not the initial scope |

A subscription per shop is a pricing hypothesis. Avoid inventing an Egyptian market price. A pilot should compare three proposed price points in interviews, measure actual support costs, and test whether owners will pay after a trial. Monthly contribution per shop equals subscription revenue minus hosting, inference, support and payment costs. Break-even shop count equals fixed monthly cost divided by positive contribution per shop. If contribution is negative, more customers make losses larger.

For a concrete hypothetical calculation, assume 30 minutes saved per day on 26 working days and an assumed time value of EGP 50 per hour. The implied time value is 0.5 × 26 × 50 = EGP 650 per month. This is an illustration, not a measured saving, wage claim or justified selling price. Validate every input. Also measure incorrect postings, owner correction time and whether the tool creates additional work.

A four-week discovery pilot could recruit ten consenting shop owners, observe existing entry tasks in week one, introduce reviewed receipt entry in week two, and compare correction rate and time in weeks three and four. Proposed success gates are hypotheses: owners can complete the core flow without assistance, every posting has an approval, no duplicate postings occur, and a majority voluntarily continue. Determine numerical commercial targets with the pilot team before collecting results.

## 3. Architecture and why each component exists
The browser displays forms and sends HTTP requests. ASP.NET Core authenticates the user, applies permission rules, reads and writes the database and requests AI inference. Python performs OCR, intent prediction, retrieval and speech recognition. The AI service has no database credential and cannot approve inventory changes. That boundary limits the consequences of a wrong model answer.

| Choice | Alternative | Why selected here | Cost or limitation |
|---|---|---|---|
| React + TypeScript | Plain JavaScript, Angular, Blazor | Component state suits the review/approval screens; TypeScript catches shape mistakes during build | Browser types cannot replace server validation |
| ASP.NET Core 10 | Node/Express, Django | User requires .NET; C# implements all business rules and auth in one application | SDK/runtime installation required |
| EF Core | Hand-written SQL | Maps typed entities to SQLite/PostgreSQL with shared application logic | Provider behavior differs; inspect generated queries |
| PostgreSQL | SQL Server, MongoDB | Relational transactions suit linked stock, ledger and approvals; Npgsql provider included | PostgreSQL deployment path was not integration-tested here |
| SQLite local demo | Mandatory database server | Low-friction submission setup and tested native path | One local database file, not proof of multi-server behavior |
| Python AI process | Reimplement every ML library in C# | Established OCR, Whisper and evaluation tooling | Extra process, network calls and failure modes |
| Cookie authentication | JWT in local storage | Same-origin browser app; HTTPOnly cookie reduces script access | Production needs HTTPS and hardened account lifecycle |
| Explicit workflow schema | Arbitrary generated code | Known fields and effects can be validated and reviewed | Only returns template currently supported |
| Exact source excerpts | Unconstrained answer generation | Every answer sentence can be traced to retrieved policy text | Less natural answers; lexical retrieval misses paraphrases |
| Human approval | Fully automatic posting | Wrong quantities or prices affect money and stock | Owner still spends review time |

Backend files: Models.cs defines data shapes and EF mapping. Program.cs configures application services and routes. OpsMonitor.cs stores recent request measurements and derives alerts. Frontend/src/main.tsx implements the screens. AI/service.py exposes inference endpoints. AI/common.py contains normalization and embedding inference. The evaluation scripts create the numerical evidence.

## 4. Business data and transaction rules
A Product stores identity, current stock, average purchase cost, lead time and safety stock. A Proposal stores a suggested purchase/sale, quantity, total, status, version and request key. A Ledger row records an approved economic effect. A Workflow stores the proposed form schema. A WorkflowRecord stores a submitted return awaiting approval. A BusinessDocument stores approved policy text. Audit records say who performed an action. Operator stores a hashed password and role.

The seed contains demo opening balances for rice and sugar. Oil starts at zero. These values are demonstration data, not transactions from a real merchant. Never call seeded balances measured customer results.

The command «اشتريت 50 كرتونة زيت بـ 12 ألف جنيه، وبعت 15 كرتونة» contains two actions. The parser understands 12 ألف as 12000. Purchase unit cost is 12000 ÷ 50 = EGP 240. After sale, quantity would be 50 − 15 = 35 cartons. Sale revenue remains unknown. The system therefore leaves the sale total empty and blocks approval until the owner supplies it. It cannot calculate profit from purchase quantity and sale quantity alone.

If the owner enters EGP 4500 as total sale revenue, cost of goods sold is 15 × 240 = EGP 3600. Gross profit is 4500 − 3600 = EGP 900. Net profit would also need expenses, finance costs, tax and other accounting adjustments. This demo reports gross profit.

Weighted average cost after a purchase equals (old stock × old average cost + new purchase total) ÷ (old stock + new quantity). A sale stores the cost at the time of approval, so later purchases do not rewrite historical sale cost. A return uses the original sale cost and proportional original revenue. Returning two of those cartons gives stock 37, net revenue 3900, COGS 3120 and gross profit 780. Total returned quantity may never exceed the original sold quantity.

Approval uses a database transaction: proposal status, product stock, ledger and audit succeed together or roll back together. A unique proposal-to-ledger relationship and status check prevent duplicate posting. A version number rejects editing an outdated proposal. A process-local write gate serializes approval requests in this demonstration. A production multi-instance design needs database-level locking/retry tests, not reliance on this gate alone.

The system flags a purchase whose unit cost differs by more than 35% from existing average cost. The owner must explicitly acknowledge the alert. Thirty-five percent is an illustrative business threshold, not a statistically validated fraud detector. A legitimate supplier price increase may trigger it.

## 5. Egyptian Arabic and intent classification
Intent means the kind of request: purchase, sale, stock question, profit question or returns. The classifier turns text into one label. It does not itself extract an amount or prove a financial fact. A separate deterministic parser extracts supported quantities and totals and creates proposals. This separation helps you explain why a model score cannot establish end-to-end accounting accuracy.

Normalization converts Arabic numerals to Western digits, removes elongation/diacritics and standardizes some letter forms. Character TF-IDF counts informative short character sequences. This can tolerate some spelling variation. Linear SVM learns boundaries separating intent classes. Logistic Regression learns class scores with a probabilistic link. The transformer candidate uses frozen multilingual sentence embeddings followed by Logistic Regression; it is not a fine-tuned large language model.

The experiment uses 150 authored examples: 100 training, 25 validation and 25 test. Validation chooses among candidates. Test is held back until after selection. Vocabulary fitting occurs on training text. The selected SVM has validation macro F1 0.880 and test macro F1 0.880, with test accuracy 0.880. Its three errors appear in the included confusion matrix. Authored phrasing and overlapping vocabulary make this a development pilot. It does not prove performance on spontaneous Egyptian speech.

The main interface accepts typed Arabic, audio uploads and a microphone recording. A voice transcript still needs review before proposal creation. Whisper Base and Small run the same Arabic transcription settings on the same eight FLEURS ar_eg clips. Four choose the candidate and four provide a held-out pilot score. These are read-speech clips, not shop recordings. Their small number gives unstable estimates. The FLEURS locale alone does not establish conversational dialect robustness.

## 6. Receipt understanding
OCR converts image pixels into text. Field extraction turns that text into useful values such as quantity and total. These are different tasks. An OCR engine can recognize most words and still confuse the one digit that matters for a purchase. The review form therefore shows raw OCR text and editable fields.

Tesseract runs locally with Arabic and English language data. The comparison also runs a Paddle PP-OCR pipeline through RapidOCR ONNX. That downloaded recognizer is a general Chinese/English model, not an Arabic-tuned Paddle configuration. This is a measured comparison of these configurations, not a claim about the strongest possible version of either library.

Forty real CORU line crops form the pilot, with twenty validation and twenty test images selected deterministically. The metric is character error rate. Paddle achieves lower validation CER and wins this crop comparison, but the selected test CER is roughly 48.9%, showing substantial errors. We retain Tesseract for the live full-page demo because an independent clean-page field extraction fixture ties the two approaches and favors the simpler deployment. These are separate tasks; the crop result does not justify claiming full-page Arabic extraction is reliable.

Eight generated English receipt pages test the plumbing: four validation, four test, with four labelled fields per page. Both configurations achieve field F1 1.0 on those clean fixtures. This says the controlled template works. It does not predict real merchant receipt performance. The live parser currently creates one reviewed product line and supports oil, rice and sugar. General multi-line invoices, discounts, tax and pack conversion require additional work.

CORU source: https://huggingface.co/datasets/abdoelsayed/CORU . Upstream describes approximately 20,000 receipts and provides separate OCR samples. This project evaluates forty crops, not the entire dataset. Retain source attribution and upstream license information with redistributed samples.

## 7. Forecasting and stock decisions
A forecast predicts an unknown future number from past observations. The research comparison uses historical US Walmart store-week sales, measured in USD. It has 45 stores. It is useful for checking the forecasting experiment, but does not train a validated Egyptian product demand predictor.

Features include prior sales at lags 1, 2, 4 and 52 weeks, the preceding rolling mean, store identity, holiday flag and calendar features. All lag features refer to earlier observations. Training has 2475 rows, validation 810 and test 810. Dates move forward. The test simulates rolling one-week forecasts: actual observations from earlier test weeks may inform later weeks. This is not a single prediction of all eighteen weeks made before the test began.

Seasonal Naive copies the same week of the previous year. Random Forest averages many decision trees. LightGBM builds trees sequentially to correct remaining errors. Validation WAPE is approximately 6.060%, 4.439% and 4.881% respectively, so Random Forest wins this comparison. Its test WAPE is 3.994%, MAE USD 41,220.98 per store-week and RMSE USD 67,082.58. The included chart aggregates all stores for readability; evaluation metrics use individual store-week rows. Aggregation can hide offsetting errors.

The live shop does not use that US monetary model to predict Egyptian carton demand. It requires at least fourteen distinct sales days and then uses a simple weekly repetition of the shop's own daily units. Average days of cover equals current stock divided by estimated daily demand, when demand is positive. Reorder threshold equals lead-time demand plus safety stock. The demo intentionally says insufficient history after one sale. Sparse days, returns, seasonal changes and supplier uncertainty need better handling before deployment.

## 8. Anomaly detection
An anomaly is an unusual observation, not automatically fraud or a mistake. The retail experiment compares a robust statistical score, Isolation Forest and an autoencoder using normalized sales ratios. An autoencoder learns to reconstruct its input; a large reconstruction error suggests unusual input. Isolation Forest isolates observations with random splits. Robust statistics measure deviation from a typical level using a scale less sensitive to extremes.

Thresholds use the 95th percentile of training scores. On 810 test rows, the approaches flag 3, 5 and 19 observations. The dataset has no verified anomaly labels. Therefore precision, recall, F1 and a best detector cannot be reported. Nineteen alerts may mean greater sensitivity or more false alarms. The live cost-change rule and operational error-rate rules are independent, explicit business controls.

## 9. Retrieval and grounded answers
RAG means retrieval-augmented generation: retrieve useful source text before writing an answer. The default implementation stops at exact evidence excerpts, giving an auditable foundation for RAG. Optional provider generation is configured separately and has not been evaluated. Do not describe default responses as generated reasoning.

BM25 ranks words using term frequency and inverse document frequency. Multilingual embeddings compare vector meanings. Hybrid reciprocal rank fusion combines the rankings without assuming equal raw score scales. The fixture contains fifteen authored bilingual policy documents, ten validation questions and ten held-out questions, with one relevant policy per query. BM25 wins with validation Recall@5 1.0 and MRR@5 0.920. Test Recall@5 is 1.0 and MRR@5 0.858. Ten simple questions cannot establish general retrieval quality.

The live retriever uses document title and text, while the small benchmark fixture measures its own authored document representation. Live questions with no lexical support abstain under BM25. A source citation tells the reader where the excerpt came from. It does not certify the policy as legally correct. The seeded 14-day returns rule is a fictional shop policy for demonstration, not an assertion of Egyptian consumer law.

Only approved company documents feed the answer. No approved Egyptian regulatory corpus has been installed. ETA's official SDK documents signed invoice submission and related APIs: https://sdk.invoicing.eta.gov.eg/einvoicingapi/ . Integration requires a separate authenticated, validated implementation. This submission does not submit tax documents or claim compliance.

## 10. Self-configuring workflows
The owner requests a returns department. The system recognizes the supported request and proposes a schema containing saleId, quantity and reason plus an owner-approval rule. The React screen renders the form from that schema. Approval activates it. A staff member can submit a record, but only an owner can approve the financial effect.

This is constrained natural-language configuration backed by a known template. The project does not execute model-generated C#, SQL or arbitrary scripts. General workflow generation would require a typed action catalogue, schema validation, access-control analysis, dry-run previews, versioning and rollback. Explain this as the product's next engineering stage rather than claiming it already exists.

## 11. AIOps and MLOps
AIOps applies analytics or AI to operating software systems. MLOps manages the lifecycle of machine-learning models, including training, evaluation, release and monitoring. They overlap, but model evaluation is not the same as service incident detection.

The implemented AIOps foundation records request duration/status in an in-memory rolling buffer, computes a five-minute request window, probes the AI service, and shows alerts. p95 latency means 95% of the measured requests finish at or below that duration. A 5xx response means a server-side failure. When at least ten requests exist, a real error rate above 5% or p95 above 3000 ms triggers a rule. These thresholds are demonstration choices, not learned service-level objectives.

The failure-simulation endpoint deliberately returns 503 and adds a clearly labelled simulated incident. It does not alter inventory and is excluded from normal error-rate calculation. AI health probes distinguish healthy and unavailable services. Monitoring uses real observed requests, but its detector is rule-based. We do not claim trained root-cause analysis or automatic self-healing. Restarting services is an operator action.

A production AIOps extension would export OpenTelemetry traces and metrics, persist logs, correlate failures by request ID, collect incident labels and compare statistical detectors with Isolation Forest or sequence models. Evaluate alert precision, incident recall, time to detect and false alerts per day on future incidents. Do not reuse the retail anomaly score as evidence of operational incident accuracy.

The model results, explicit selection criteria and saved artifacts are an initial MLOps foundation. A full platform would add a model registry, dataset versioning, release approvals, drift monitoring and rollback. Data drift means inputs have changed. Concept drift means the relationship between input and target has changed. Neither guarantees degraded quality by itself; monitor labelled outcomes when possible.

## 12. Security, reliability and current limits
Passwords use the framework's password hasher. Cookies use HTTPOnly and SameSite Strict. Mutating API calls require a custom header and reject a mismatched Origin. The owner policy protects approval and operational endpoints. File size and image checks limit upload handling. User input is never executed as program code. A shared database transaction preserves financial consistency.

This is still a local academic application. Production requirements include HTTPS, secret management, account enrollment/recovery, rate limits, persistent authentication keys, stronger concurrency testing, backup and restore drills, malware scanning, observability retention and multi-tenant isolation. Current startup uses EnsureCreated for convenience; production needs reviewed EF migrations. PostgreSQL is configured and compiles but was not exercised in the integration environment.

Do not expose the AI service publicly. It is designed as an internal inference service. The Compose file exposes only the browser-facing API on localhost. The application does not promise offline cloud synchronization or legal compliance for regulated sectors.

## 13. Verification and reproduction
The C# build completed with zero warnings and errors. Twenty-five application assertions passed against a fresh SQLite database. They cover authorization, Arabic compound parsing, missing prices, no mutation before approval, weighted costing, idempotency, stale edits, returned quantities, anomaly acknowledgement, source excerpts, insufficient history, AIOps simulation and audit existence. These are selected regression checks, not an exhaustive security audit.

The browser test opened eight screens, exercised receipt upload, checked JavaScript page errors and inspected desktop/mobile sizes. The application results and browser report are in results. Tests do not prove that every possible receipt or Arabic utterance works.

To reproduce ML comparisons, install ai/requirements-evaluation.txt and download embeddings and both voice models. Run `python ai/evaluate.py`, `python ai/evaluate_ocr.py`, `python ai/evaluate_receipt_fields.py` and `python ai/evaluate_speech.py`. These may overwrite results. The selected OCR crop fixtures and audio samples are bundled. Random seeds help repeatability but library versions, CPU instructions and threading can change timings or small numerical details.

For isolated application testing start the AI service on8091, then run the API at5082 with `ConnectionStrings__Sqlite` pointing to a new test database. From the parent of TajerOS run `python TajerOS/tests/integration.py`. Never point this test at real customer data. The included UI verification report records the author's run; its browser automation harness depends on the authoring environment and is not required to run the app.

## 14. Questions you should be able to answer
**Why did the transformer lose?** On this small authored intent fixture, frozen multilingual embeddings plus a linear classifier achieved lower validation F1 than character SVM. That does not establish a universal weakness of transformers, and we did not fine-tune one end to end.

**Why use a separate Python process if the backend must be .NET?** All business APIs, database ownership, authorization and financial rules are C#. Python supplies specialized inference through HTTP. It cannot post transactions. This matches the chosen architecture.

**What is actually self-building?** The returns form and approval configuration derive from a supported natural-language request and render dynamically. General arbitrary department generation remains future work.

**Where are the real results?** The included JSON files and presentation charts report actual runs. Intent and retrieval inputs are authored fixtures. Retail, CORU and FLEURS are external datasets. Field extraction uses generated clean receipts. Every score must be stated with its data source.

**Why not show anomaly accuracy?** There are no verified anomaly labels. Alert count is observable, but correct detection cannot be determined without ground truth.

**Can it calculate profit from the original example?** Only after the sale revenue is supplied. Purchase cost alone gives unit cost and remaining quantity, not profit.

**Why not claim every Egyptian business can use it?** Different industries have different workflows, units, legal obligations and data quality. A small retailer is the tested demonstration scope.

**Does AIOps heal failures?** No. It measures requests, checks service health and flags conditions. The owner can simulate a failure without affecting stock. Automated remediation requires additional controls and validation.

**What would you build next?** Collect consented merchant examples, improve Arabic receipt extraction, expand typed workflow templates, add PostgreSQL concurrency tests and validate commercial value in a small pilot.

## 15. Plain-language glossary

| Term | Simple meaning | In this project |
|---|---|---|
| AI | Artificial intelligence: software that performs tasks such as recognizing speech or classifying text. | TajerOS predicts intent, but approval rules remain explicit. |
| ML | Machine learning: learning numerical patterns from examples. | The SVM learns from labelled commands. |
| Model | A saved set of learned parameters and a prediction procedure. | results/intent.joblib contains the selected classifier. |
| Training | Using examples to fit a model. | 100 authored commands fit the intent models. |
| Validation | Examples used to choose a model or settings. | 25 commands choose the intent candidate. |
| Test set | Examples reserved for final evaluation after selection. | 25 different commands provide the reported test score. |
| Ground truth | The reference answer used to judge a prediction. | A human-written intent label or receipt transcription. |
| Label | A category or target attached to an example. | purchase is a label. |
| Feature | A numerical input supplied to a model. | Last week's sales is a forecast feature. |
| Inference | Using an already trained model on new input. | Predicting a clerk's command intent. |
| Overfitting | Learning peculiarities of training examples that do not generalize. | Memorizing repeated receipt layouts can look deceptively accurate. |
| Generalization | Working on genuinely new examples. | Success on real shops requires separate customer tests. |
| Data leakage | Information from validation/test targets improperly influencing training. | Using future sales to form a lag would leak information. |
| Baseline | A simple reference approach. | Seasonal Naive copies last year's week. |
| Hyperparameter | A setting chosen before fitting. | Number of trees in Random Forest. |
| Seed | A number controlling pseudorandom choices. | 42 helps repeat the experiment. |
| NLP | Natural language processing: computation on human language. | Recognizing purchase intent in Arabic. |
| Intent | The kind of action or question a user expresses. | sale versus purchase. |
| Normalization | Applying consistent text transformations. | Converting ١٢ to 12. |
| Token | A unit of text processed by an algorithm. | A word in BM 25 or character sequence in TF-IDF. |
| TF-IDF | A weighting that favors informative text units over common ones. | Character features for the intent classifier. |
| SVM | Support Vector Machine: a classifier that separates classes with decision boundaries. | Selected small intent model. |
| Logistic Regression | A linear classifier using a logistic probability mapping. | An alternative intent candidate. |
| Transformer | A neural architecture that models relationships among tokens. | A frozen multilingual embedding candidate. |
| Embedding | A numerical vector representing meaning or other information. | Similar policies may have nearby vectors. |
| Frozen | Parameters stay unchanged during the experiment. | The sentence encoder is not fine-tuned. |
| Fine-tuning | Updating a pretrained model using task-specific examples. | A future Egyptian speech improvement strategy. |
| OCR | Optical character recognition: reading text from pixels. | Receipt image to text. |
| Tesseract | An open-source OCR engine. | Live full-page receipt reader. |
| PaddleOCR | An OCR toolkit with trained recognition/detection models. | Compared via RapidOCR ONNX configuration. |
| CER | Character error rate: substitutions, deletions and insertions divided by reference characters. | Lower is better; it can exceed 1. |
| WER | Word error rate: analogous edit errors divided by reference words. | Measures speech transcription mistakes. |
| Precision | Correct positive predictions divided by all positive predictions. | Requires verified labels. |
| Recall | Correct positive predictions divided by all actual positives. | How many relevant events the detector finds. |
| F 1 | Harmonic mean of precision and recall. | Balances both kinds of classification error. |
| Macro F 1 | Unweighted average of each class's F 1. | Treats each intent as equally important. |
| Accuracy | Correct labels divided by total examples. | 22 correct out of 25 equals 0.88. |
| Confusion matrix | Counts actual classes against predicted classes. | Shows which intents get confused. |
| MAE | Mean absolute error: average absolute prediction miss. | Forecast errors measured in USD per store-week. |
| RMSE | Square root of mean squared error. | Larger misses receive more influence than with MAE. |
| WAPE | Sum of absolute errors divided by sum of absolute actual values. | A percentage-style forecasting error; zero denominator is undefined. |
| Lag | An earlier observation used as a feature. | Sales 52 weeks earlier. |
| Rolling origin | Move prediction time forward and use information available at each point. | Earlier test actuals may feed later weekly forecasts. |
| Random Forest | Many decision trees whose outputs are averaged or voted. | Selected retail forecast candidate. |
| LightGBM | Gradient-boosted tree software. | Alternative forecast candidate. |
| Anomaly | An observation that differs from typical patterns. | A large price change may be legitimate. |
| Isolation Forest | A method that isolates unusual points using random splits. | Compared without ground-truth anomaly labels. |
| Autoencoder | A network trained to reconstruct its own inputs. | High reconstruction error can signal unusual input. |
| Threshold | A boundary that triggers a decision. | 35% cost deviation prompts acknowledgement. |
| RAG | Retrieval-augmented generation: find evidence before composing an answer. | Default app returns excerpts; generation is optional. |
| BM 25 | A keyword ranking method using frequency and rarity. | Selected policy retrieval method. |
| Cosine similarity | Similarity based on the angle between vectors. | Used with normalized sentence embeddings. |
| RRF | Reciprocal Rank Fusion: combines rank positions from search methods. | Hybrid retrieval candidate. |
| Recall@5 | Fraction of relevant reference items found within the first 5 results. | With one relevant item, this is top 5 hit rate. |
| MRR@5 | Average inverse rank of the first relevant result within the first 5. | A first-place answer contributes 1, second contributes 0.5. |
| Citation | A link or identifier connecting an answer to evidence. | The policy document and its excerpt. |
| Hallucination | An unsupported generated claim. | Exact excerpts reduce this particular risk. |
| Abstention | Declining to answer when evidence is insufficient. | No approved document support leads to no answer. |
| LLM | Large language model: a large neural text model. | Optional external generation only. |
| Prompt | Instructions and input sent to a generative model. | Question plus retrieved evidence. |
| Prompt injection | Untrusted input attempting to override model instructions. | A document could contain malicious commands. |
| ERP | Enterprise resource planning: connected business records/workflows. | TajerOS demonstrates a small subset. |
| SKU | Stock keeping unit: a distinct tracked product. | oil is a demo product identifier. |
| Inventory | Quantity and value of goods held. | 35 oilcartons after the example sale. |
| Revenue | Money earned from sales before related cost deductions. | 4500 EGP from the sample sale. |
| COGS | Cost of goods sold. | 3600 EGP for 15 cartons at 240 each. |
| Gross profit | Revenue minus cost of goods sold. | 900 EGP before expenses and tax. |
| Net profit | Profit after relevant expenses and other accounting adjustments. | Not calculated by this demo. |
| Weighted average cost | Inventory cost averaged by quantities and purchase values. | Prevents treating all purchases as the latest price. |
| Lead time | Delay between placing an order and receiving stock. | Seeded oil policy says 3 days. |
| Safety stock | Extra stock held to absorb uncertainty. | Seeded 10 cartons, an assumption. |
| Stockout | Demand arrives when usable stock is unavailable. | Forecasting aims to reduce this risk. |
| Ledger | A history of approved economic effects. | Purchase, sale and return entries. |
| Audit trail | A history of who did what and when. | Owner approval records. |
| Idempotency | Repeating a request has the same effect as doing it once. | Double-clicking approval does not double inventory. |
| Concurrency | Operations happening at overlapping times. | Two owners may try to approve together. |
| Transaction | A group of database changes that succeed or fail together. | Stock, ledger and approval status stay consistent. |
| Rollback | Undoing uncommitted transaction changes after failure. | An invalid sale leaves stock unchanged. |
| Schema | A definition of data fields and types. | The generated returns form has 3 fields. |
| State machine | Allowed states and transitions for a process. | Pending proposal can become approved or rejected. |
| API | Application programming interface: defined operations between programs. | Browser calls /api/proposals. |
| HTTP | The request/response protocol used by the web. | POST submits a proposal. |
| JSON | A structured text data format. | The workflow schema and API responses. |
| DTO | Data transfer object: a request/response data shape. | Approval input includes version and acknowledgement. |
| ASP.NET Core | The .NET web application framework. | Hosts business endpoints. |
| C# | The programming language used for the backend. | Implements authorization and money rules. |
| EF Core | Object-relational mapper for .NET. | Maps Product objects to database rows. |
| PostgreSQL | A relational database server. | Configured deployment database. |
| SQLite | An embedded relational database stored in a file. | Tested local demonstration database. |
| React | A browser UI library built around components. | Renders the review and workflow screens. |
| TypeScript | JavaScript with compile-time type checking. | Helps catch UI data-shape mistakes. |
| Vite | Frontend development and build tooling. | Produces static assets in wwwroot. |
| Authentication | Checking who the user is. | Password login. |
| Authorization | Checking what the user may do. | Staff cannot approve a purchase. |
| Hash | A one-way transformation used in password storage. | The database stores password hashes. |
| Cookie | Browser-managed data attached to matching requests. | Carries the authenticated session. |
| HTTPOnly | Cookie attribute preventing normal JavaScript access. | Reduces session exposure to scripts. |
| CSRF | Cross-site request forgery: tricking a browser into an unwanted action. | SameSite, origin checks and custom headers help protect writes. |
| CORS | Browser policy for cross-origin API access. | No cross-origin API access is enabled here. |
| CSP | Content Security Policy: rules limiting browser resource execution. | The app emits a security policy header. |
| AIOps | Analytics/AI applied to operating software systems. | Current foundation monitors requests with explicit rules. |
| MLOps | Practices for developing, releasing and monitoring models. | Saved experiments are a first step. |
| Telemetry | Measurements emitted by running software. | Request duration and status. |
| Latency | Time taken to complete a request. | Measured in milliseconds. |
| p 95 | The 95 thpercentile of a set of values. | A tail-latency indicator, not the average. |
| Error rate | Failed requests divided by observed requests. | 5 xxrate in the monitoring window. |
| Health probe | A request checking whether a service responds. | API calls AI/health. |
| SLO | Service-level objective: a target for reliability or speed. | Production thresholds need an agreed target. |
| MTTR | Mean time to recovery or repair, depending on the agreed definition. | Requires real incident timing to measure. |
| Drift | A change in inputs or their relationship to outcomes. | A new supplier receipt layout changes OCR inputs. |
| Model registry | A controlled catalogue of model versions and metadata. | Future lifecycle feature. |
| Canary release | Expose a new version to a small share of traffic first. | Potential model rollout strategy. |
| Container | A packaged process environment. | Docker images hold API and AI dependencies. |
| Docker Compose | A definition for running related containers together. | Starts PostgreSQL,AIandAPI. |
| B 2 B | A business sells to another business. | TajerOS subscription sold to a shop. |
| B 2 B 2 C | A business serves consumers through another business. | Future merchant/customer flows. |
| B 2 C | A business sells directly to a consumer. | Not the primary shop-ERP route. |
| B 2 G | A business sells to government. | Possible later procurement route. |
| G 2 B | Government provides a service to businesses. | Government-operated digitization service. |
| G 2 C | Government provides a service to citizens. | Different operator and beneficiary model. |
| SaaS | Software as a service: hosted software accessed over a network. | A possible commercial delivery model. |
| Churn | Customers stopping use or payment. | Measure during a future pilot. |
| Unit economics | Revenue and variable cost for one customer/unit. | Contribution per shop. |
| Product-market fit | Evidence that a product satisfies a market sufficiently to sustain demand. | Not established by this submission. |

## 16. Complete measured comparison table

Different metrics and datasets cannot be combined into one overall accuracy ranking. Values below retain their native fraction/count units.

| Task | Candidate | Metric | Value | Direction |
|---|---|---|---|---|
| Intent | TF-IDF + Linear SVM | validationMacroF1 | 0.879596 | higher |
| Intent | TF-IDF + Logistic Regression | validationMacroF1 | 0.840000 | higher |
| Intent | Multilingual transformer + LR | validationMacroF1 | 0.705628 | higher |
| Forecast | Seasonal Naive (52 weeks) | WAPE | 0.060602 | lower |
| Forecast | Random Forest | WAPE | 0.044387 | lower |
| Forecast | LightGBM | WAPE | 0.048814 | lower |
| Anomaly | Robust statistical rule | testAlerts | 3 | neither |
| Anomaly | Isolation Forest | testAlerts | 5 | neither |
| Anomaly | Autoencoder | testAlerts | 19 | neither |
| Retrieval | BM25 | validationRecall5 | 1.000000 | higher |
| Retrieval | Multilingual embeddings | validationRecall5 | 0.800000 | higher |
| Retrieval | Hybrid RRF | validationRecall5 | 0.900000 | higher |
| OCR crops | Tesseract Arabic+English | validationCER | 0.451697 | lower |
| OCR crops | Paddle PP-OCR via RapidOCR ONNX | validationCER | 0.352480 | lower |
| Speech | Whisper Base | validationWER | 0.436782 | lower |
| Speech | Whisper Small | validationWER | 0.241379 | lower |
| Receipt fields | Tesseract full page | validationFieldF1 | 1.000000 | higher |
| Receipt fields | Paddle PP-OCR full page | validationFieldF1 | 1.000000 | higher |

Speech selection: Whisper Small. Held-out WER 0.127660. Selected OCR crop test CER 0.488739. Receipt-field test F1 1.000000.

## 17. API and code reading map

| Endpoint | Purpose | What to explain |
|---|---|---|
| POST /api/login | Check hashed password and issue cookie | Authentication establishes identity |
| GET /api/dashboard | Load current records and derived totals | Totals come from approved ledger records |
| POST /api/commands/propose | Call AI and create pending suggestions | No stock mutation happens here |
| POST /api/proposals | Submit manually reviewed transaction | Server validates the supported shape |
| PUT /api/proposals/{id} | Edit pending quantity and total | Version checks reject stale edits |
| POST /api/proposals/{id}/approve | Post purchase/sale | Owner authorization and atomic transaction |
| POST /api/proposals/{id}/reject | Reject pending proposal | Rejection leaves inventory unchanged |
| POST /api/receipts/read | Read uploaded image | OCR output remains unverified evidence |
| POST /api/voice/transcribe | Read uploaded audio | Transcript review precedes business action |
| POST /api/workflows/propose | Build known returns schema | Constrained configuration, no generated executable code |
| POST /api/workflows/{id}/approve | Activate reviewed schema | Only owner can activate |
| POST /api/workflows/{id}/records | Submit a return form | Submission does not restock |
| POST /api/workflow-records/{id}/approve | Execute return | Original sale cost and return limits apply |
| POST /api/documents | Add approved company policy | Owner controls knowledge corpus |
| POST /api/ask | Retrieve company evidence | No business writes allowed |
| GET /api/forecast/{product} | Estimate stock needs | Refuses insufficient history |
| GET /api/benchmarks | Load measured experiment results | Research evidence is separate from shop data |
| GET /api/ops | Request monitoring and AI health | Owner-only operational view |
| POST /api/ops/simulate-failure | Safe failure demonstration | Returns503, excludes simulation from real error-rate calculation |
| GET /api/audit | Read action history | Inspect who approved each change |

Read code in this order: Models.cs, startup/authentication in Program.cs, proposal creation, proposal approval, return approval, OpsMonitor.cs, then AI/service.py and frontend/src/main.tsx. The UI's `api` function is the shared HTTP helper. `action` manages busy/error state and refreshes data. `uploadReceipt` sends multipart form data. `submitCommand` asks for proposals. Each visible workflow state comes from the backend response.

In service.py, `interpret` combines learned intent with constrained parsing; `ocr` calls Tesseract and extracts fields; `ask` retrieves approved text; `forecast` calculates a simple baseline; `transcribe` decodes bounded audio using FFmpeg and executes Whisper. FFmpeg runs with an argument array, without shell interpretation. Model files load only from configured local paths. Do not load untrusted joblib files: Python object serialization is not a safe interchange format for arbitrary uploads.

## 18. Study plan before the defense

1. Read sections1–4 and explain the purchase/sale example aloud without notes.
2. Run the README demonstration from a fresh database. Practice a missing-price rejection and duplicate approval.
3. Learn the difference between classification, extraction, prediction and retrieval. They solve different problems.
4. Read each result chart with its dataset, metric, split and limitation. Practice saying why the selected candidate won only this comparison.
5. Explain the .NET/Python boundary and the transaction/approval safeguards.
6. Demonstrate AIOps, then state exactly which automation remains future work.
7. Use the glossary when a term is unfamiliar. You do not need to memorize every source line; you should know where each responsibility lives.
