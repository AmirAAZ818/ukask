// Real questions a student would actually bring to the regulations, they double
// as a hint about what this corpus can and cannot answer.
const SUGGESTIONS = [
  "شرایط حذف اضطراری درس چیست؟",
  "حداکثر سنوات مجاز تحصیل در مقطع کارشناسی چقدر است؟",
  "مشروطی چه پیامدی برای دانشجو دارد؟",
  "شرایط مهمان شدن در دانشگاه دیگر چیست؟",
];

export default function EmptyState({ onPick }) {
  return (
    <div className="empty">
      <p className="empty__lead">دربارهٔ آیین‌نامه‌های دانشگاه بپرسید.</p>
      <p className="empty__sub">
        پاسخ‌ها از متن آیین‌نامه‌های مصوب دانشگاه شهید باهنر کرمان بیرون کشیده
        می‌شوند و هر پاسخ، ماده و صفحهٔ مرجع خود را همراه دارد.
      </p>

      <div className="empty__label">نمونه پرسش</div>
      <div className="empty__chips">
        {SUGGESTIONS.map((text) => (
          <button key={text} className="chip" onClick={() => onPick(text)}>
            {text}
          </button>
        ))}
      </div>
    </div>
  );
}