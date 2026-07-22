import { useEffect, useRef, useState } from "react";

const LINKS = [
  { label: "گیت‌هاب", href: "https://github.com/AmirAAZ818" },
  { label: "لینکدین", href: "https://www.linkedin.com/in/amirhossein-abolhasani/" },
  { label: "ایمیل", href: "mailto:a.abolhasani.ac@gmail.com" },
];

// Course-project credit line. Clicking the name toggles a small menu of
// titles only, closes on an outside click, Escape, or picking a link.
export default function Footer() {
  const [open, setOpen] = useState(false);
  const wrapRef = useRef(null);

  useEffect(() => {
    if (!open) return;
    function onDocClick(e) {
      if (wrapRef.current && !wrapRef.current.contains(e.target)) setOpen(false);
    }
    function onKeyDown(e) {
      if (e.key === "Escape") setOpen(false);
    }
    document.addEventListener("mousedown", onDocClick);
    document.addEventListener("keydown", onKeyDown);
    return () => {
      document.removeEventListener("mousedown", onDocClick);
      document.removeEventListener("keydown", onKeyDown);
    };
  }, [open]);

  return (
    <footer className="footer">
      <span>© ۲۰۲۶ · پروژهٔ پایانی درس پردازش زبان طبیعی توسط</span>
      <div className="footer__contact" ref={wrapRef}>
        <button
          className="footer__name"
          onClick={() => setOpen((v) => !v)}
          aria-expanded={open}
        >
          امیرحسین ابوالحسنی
        </button>
        {open && (
          <div className="footer__tip" role="menu">
            {LINKS.map((link) => (
              <a
                key={link.label}
                role="menuitem"
                href={link.href}
                target={link.href.startsWith("mailto:") ? undefined : "_blank"}
                rel="noreferrer"
                onClick={() => setOpen(false)}
              >
                {link.label}
              </a>
            ))}
          </div>
        )}
      </div>
    </footer>
  );
}