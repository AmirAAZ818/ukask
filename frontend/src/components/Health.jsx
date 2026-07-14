const LABELS = {
  checking: { text: "در حال بررسی سرور", modifier: "" },
  ok: { text: "آماده", modifier: "health__dot--ok" },
  down: { text: "سرور در دسترس نیست", modifier: "health__dot--down" },
};

export default function Health({ status }) {
  const { text, modifier } = LABELS[status] ?? LABELS.checking;

  return (
    <div className="health">
      <span className={`health__dot ${modifier}`} />
      <span>{text}</span>
    </div>
  );
}