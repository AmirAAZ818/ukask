// The regulations themselves are written with Persian numerals, so the UI
// speaks the same way. Latin digits only survive in file names.

const PERSIAN_DIGITS = ["۰", "۱", "۲", "۳", "۴", "۵", "۶", "۷", "۸", "۹"];

export function toPersianDigits(value) {
  return String(value).replace(/\d/g, (d) => PERSIAN_DIGITS[Number(d)]);
}

export function toPercent(similarity) {
  return toPersianDigits(Math.round(similarity * 100));
}