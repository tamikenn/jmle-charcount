// jmle-charcount — 計数規則の JS 実装(count.py の忠実な移植)。
// ブラウザ(count.html)と Node の双方から使う。外部依存なし。
const BODY_CLASSES = ["kanji", "hiragana", "katakana", "latin", "digit"];
const GREEK_LOWER = "αβγδεζηθικλμνξοπρστυφχψω";
const PUNCT_EXTRA = "、。「」『』〈〉《》【】・…―";
const SYMBOL_EXTRA = "℃％±×÷≦≧〒";
// Python str.isdigit() が True だが Unicode カテゴリ Nd でない 128 文字(上付き・丸数字等)
const DIGIT_EXTRA = "²³¹፩፪፫፬፭፮፯፰፱᧚⁰⁴⁵⁶⁷⁸⁹₀₁₂₃₄₅₆₇₈₉①②③④⑤⑥⑦⑧⑨⑴⑵⑶⑷⑸⑹⑺⑻⑼⒈⒉⒊⒋⒌⒍⒎⒏⒐⓪⓵⓶⓷⓸⓹⓺⓻⓼⓽⓿❶❷❸❹❺❻❼❽❾➀➁➂➃➄➅➆➇➈➊➋➌➍➎➏➐➑➒𐩀𐩁𐩂𐩃𐹠𐹡𐹢𐹣𐹤𐹥𐹦𐹧𐹨𑁒𑁓𑁔𑁕𑁖𑁗𑁘𑁙𑁚🄀🄁🄂🄃🄄🄅🄆🄇🄈🄉🄊";

function charClass(ch) {
  const o = ch.codePointAt(0);
  if (" 　\t\n\r\f\v".includes(ch)) return "whitespace";
  if (o >= 0x3040 && o <= 0x309f) return "hiragana";
  if ((o >= 0x30a0 && o <= 0x30ff) || (o >= 0x31f0 && o <= 0x31ff)) return "katakana";
  if ((o >= 0x4e00 && o <= 0x9fff) || (o >= 0x3400 && o <= 0x4dbf) ||
      (o >= 0xf900 && o <= 0xfaff) || (o >= 0x20000 && o <= 0x2fa1f) ||
      "々〆〤ヶ".includes(ch)) return "kanji";
  if ((o >= 0x41 && o <= 0x5a) || (o >= 0x61 && o <= 0x7a) ||
      (o >= 0xff21 && o <= 0xff3a) || (o >= 0xff41 && o <= 0xff5a) ||
      (o >= 0xc0 && o <= 0x24f) || GREEK_LOWER.includes(ch)) return "latin";
  // Python str.isdigit() 相当 = Nd + DIGIT_EXTRA(数字性はあるが Nd でない文字。分数 ½ 等は含まない)
  if (/\p{Nd}/u.test(ch) || DIGIT_EXTRA.includes(ch) ||
      (o >= 0xff10 && o <= 0xff19)) return "digit";
  if (/\p{P}/u.test(ch) || PUNCT_EXTRA.includes(ch)) return "punct";
  if (/\p{S}/u.test(ch) || SYMBOL_EXTRA.includes(ch)) return "symbol";
  return "other";
}

function countText(text) {
  let nfc = (text || "").normalize("NFC");
  nfc = Array.from(nfc).filter((ch) => !/\p{Cc}|\p{Cf}/u.test(ch)).join("");
  const noWs = nfc.replace(/\s+/gu, "");

  const byClass = {};
  for (const ch of nfc) {
    const k = charClass(ch);
    byClass[k] = (byClass[k] || 0) + 1;
  }
  const body = BODY_CLASSES.reduce((s, c) => s + (byClass[c] || 0), 0);
  return {
    body,                                    // ★主指標
    printed_total: Array.from(noWs).length,  // 副指標(句読点・記号込み・空白除外)
    with_whitespace: Array.from(nfc).length,
    by_class: byClass,
    kanji_pct: body ? Math.round(((byClass.kanji || 0) / body) * 1000) / 10 : 0,
    latin_pct: body ? Math.round(((byClass.latin || 0) / body) * 1000) / 10 : 0,
  };
}

if (typeof module !== "undefined") module.exports = { charClass, countText, BODY_CLASSES };
