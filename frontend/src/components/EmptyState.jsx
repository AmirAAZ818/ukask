import Logo from "./Logo";
import { toPersianDigits } from "../format";

// A short, honest explanation of what happens after a question is sent, this
// is the only place in the app that explains the retrieval step at all.
const STEPS = [
  {
    title: "بپرسید",
    body: "سؤال خود را دربارهٔ مقررات دانشگاه به فارسی بنویسید.",
  },
  {
    title: "جست‌وجو در آیین‌نامه‌ها",
    body: "سامانه در متن آیین‌نامه‌های مصوب دنبال پاسخ می‌گردد.",
  },
  {
    title: "پاسخ مستند",
    body: "پاسخ به همراه مادهٔ مرجع و صفحهٔ سند نمایش داده می‌شود.",
  },
];

// Grouped rather than one flat row, real questions a student would bring to
// the regulations, they double as a hint about what this corpus covers.
const SUGGESTION_GROUPS = [
  {
    label: "آموزشی",
    items: [
      "شرایط حذف اضطراری درس چیست؟",
      "حداکثر سنوات مجاز تحصیل در مقطع کارشناسی چقدر است؟",
      "مشروطی چه پیامدی برای دانشجو دارد؟",
    ],
  },
  {
    label: "دانشجویی",
    items: [
      "شرایط مهمان شدن در دانشگاه دیگر چیست؟",
      "شرایط دریافت مرخصی تحصیلی چیست؟",
      "نحوهٔ درخواست انتقالی دانشجو چگونه است؟",
    ],
  },
];

export default function EmptyState({ onPick }) {
  return (
    <div className="empty">
      {/* <div className="empty__mark">
        <Logo size={44} />
      </div> */}

      <p className="empty__lead">دربارهٔ آیین‌نامه‌های دانشگاه بپرسید.</p>
      <p className="empty__sub">
        پاسخ‌ها از متن آیین‌نامه‌های مصوب دانشگاه شهید باهنر کرمان بیرون کشیده
        می‌شوند و هر پاسخ، ماده و صفحهٔ مرجع خود را همراه دارد.
      </p>
{/* 
      <div className="empty__steps">
        {STEPS.map((step, i) => (
          <div className="empty__step" key={step.title}>
            <span className="empty__step-index">{toPersianDigits(i + 1)}</span>
            <div>
              <div className="empty__step-title">{step.title}</div>
              <div className="empty__step-body">{step.body}</div>
            </div>
          </div>
        ))}
      </div> */}

      <div className="empty__groups">
        {SUGGESTION_GROUPS.map((group) => (
          <div className="empty__group" key={group.label}>
            <div className="empty__label">{group.label}</div>
            <div className="empty__chips">
              {group.items.map((text) => (
                <button key={text} className="chip" onClick={() => onPick(text)}>
                  {text}
                </button>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}