// Grouped rather than one flat row: real questions a student would bring to
// the regulations, doubling as a hint about what this corpus covers.
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
      <p className="empty__lead">دربارهٔ آیین‌نامه‌های دانشگاه بپرسید.</p>
      <p className="empty__sub">
        پاسخ‌ها از متن آیین‌نامه‌های مصوب دانشگاه شهید باهنر کرمان بیرون کشیده
        می‌شوند و هر پاسخ، ماده و صفحهٔ مرجع خود را همراه دارد.
      </p>

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