# fraud-service · SDA-AIE-113 labs

The hands-on project of **SDA-AIE-113 · Software Engineering Practices for AI Systems**
(SDAIA Academy). You take a fraud-scoring model from a notebook to a tested, containerised
service with a CI/CD pipeline, one lab at a time, with an AI coding agent as your tutor.

Workshop site: https://aie113.ibrahimalshehri.sa · Arabic: https://aie113.ibrahimalshehri.sa/ar/ · [النسخة العربية من هذا الدليل](#بالعربية)

## 1. Fork and open

1. Click **Fork** at the top of this page. Keep the name `fraud-service`.
2. Clone your fork and set it up (Python 3.12 or newer):

       git clone https://github.com/YOUR-USERNAME/fraud-service.git
       cd fraud-service
       python -m venv .venv
       source .venv/bin/activate          # Windows PowerShell: .venv\Scripts\Activate.ps1
       pip install -e ".[dev]"

3. Open the folder in your coding agent: Claude Code, GitHub Copilot (agent mode), Cursor,
   Codex or similar. They all read [AGENTS.md](AGENTS.md), which tells the agent to teach you
   as you go instead of silently writing the code.

## 2. Pick a lab and say one sentence

    Read AGENTS.md and labs/lab-2b.md, then teach me Lab 2b one step at a time.

Each lab guide also lists a prompt per step, if you prefer to drive.

| Lab | What you build | Starting point |
|---|---|---|
| [Lab 1](labs/lab-1.md) | Refactor the notebook into a clean package | `lab1-start` |
| [Lab 2a](labs/lab-2a.md) | Build the prediction API | `lab2a-start` |
| [Lab 2b](labs/lab-2b.md) | Harden the API | `lab2b-start` |
| [Lab 3](labs/lab-3.md) | Containerise the fraud service | `lab3-start` |
| [Lab 4](labs/lab-4.md) | Build the test suite | `lab4-start` |
| [Lab 5](labs/lab-5.md) | Build the pipeline | `lab5-start` |
| [Lab 6](labs/lab-6.md) | Harden config, secrets and logs | `lab6-start` |

## 3. Start at a later lab, or catch up

Each lab's starting point is a tag. To bring your project to one (for example Lab 3), ask
your agent, or run:

    git remote add upstream https://github.com/snow10100/fraud-service.git    # once
    git fetch upstream --tags
    git checkout lab3-start -- .
    git commit -m "chore: start from the Lab 3 starting point"

Your own extra files, such as `BENCHMARKS.md`, are kept.

## What is in here

| Path | What |
|---|---|
| `src/fraud_service/` | The service you build, layer by layer |
| `legacy/notebook_v1.py` | The inherited script with a silent bug: Lab 1 starts here |
| `data/`, `models/`, `payloads/` | Synthetic transactions, the trained model, request bodies (no real customer data) |
| `labs/lab-*.md`, `labs/ar/` | One guide per lab, in English and Arabic |
| `labs/handouts/<lab>/` | The exact files each lab hands out, at their project paths |
| `AGENTS.md` | Instructions for your coding agent (`CLAUDE.md` and `.github/copilot-instructions.md` point to it) |

If scoring seems to hang on a machine with many cores (common under WSL), run
`export OMP_NUM_THREADS=1` (PowerShell: `$env:OMP_NUM_THREADS=1`) and try again.

---

<div dir="rtl" lang="ar">

## بالعربية

المشروع العملي لورشة **ممارسات هندسة البرمجيات لأنظمة الذكاء الاصطناعي (SDA-AIE-113)** في
أكاديمية سدايا. تنقل نموذج رصد احتيال من دفتر (notebook) إلى خدمة مختبرة داخل حاوية، مع خط
أتمتة CI/CD، مختبرًا تلو الآخر، ويكون وكيل البرمجة الذكي معلّمك أثناء العمل.

1. اضغط **Fork** أعلى الصفحة، واترك الاسم `fraud-service`.
2. انسخ المستودع إلى جهازك وثبّت المتطلبات (الأوامر في القسم 1 أعلاه، وتحتاج Python 3.12 أو أحدث).
3. افتح المجلد في وكيل البرمجة الذي تستخدمه. الوكيل يقرأ الملف AGENTS.md الذي يطلب منه أن يشرح لك كل خطوة بدل أن يكتب الكود بصمت.
4. اختر مختبرًا واكتب للوكيل جملة واحدة، مثل:

</div>

    Read AGENTS.md and labs/ar/lab-2b.md, then teach me Lab 2b one step at a time. Reply in Arabic.

<div dir="rtl" lang="ar">

| المختبر | ما تبنيه | نقطة البداية |
|---|---|---|
| [المختبر 1](labs/ar/lab-1.md) | إعادة هيكلة الدفتر إلى حزمة نظيفة | `lab1-start` |
| [المختبر 2أ](labs/ar/lab-2a.md) | بناء واجهة التنبؤ | `lab2a-start` |
| [المختبر 2ب](labs/ar/lab-2b.md) | تقوية الواجهة | `lab2b-start` |
| [المختبر 3](labs/ar/lab-3.md) | وضع خدمة رصد الاحتيال في حاوية | `lab3-start` |
| [المختبر 4](labs/ar/lab-4.md) | بناء مجموعة الاختبارات | `lab4-start` |
| [المختبر 5](labs/ar/lab-5.md) | بناء خط الأتمتة | `lab5-start` |
| [المختبر 6](labs/ar/lab-6.md) | تحصين الإعدادات والأسرار والسجلات | `lab6-start` |

لتبدأ من مختبر لاحق أو تلحق بالمجموعة، اطلب من وكيلك أن ينقل مشروعك إلى الوسم (tag) الخاص
بذلك المختبر، أو نفّذ الأوامر في القسم 3 أعلاه. ملفاتك الخاصة مثل `BENCHMARKS.md` تبقى كما هي.

إذا بدا حساب الدرجات متوقفًا على جهاز كثير الأنوية (يحدث كثيرًا مع WSL)، نفّذ
`export OMP_NUM_THREADS=1` (وفي PowerShell: `$env:OMP_NUM_THREADS=1`) ثم أعد المحاولة.

</div>

## أكاديمية سدايا

[منصة أكاديمية سدايا «أذكى X»](https://athkax.sdaia.gov.sa/)
