window.MathJax = {
  tex: {
    inlineMath: [["\\(", "\\)"]],
    displayMath: [["\\[", "\\]"]],
    processEscapes: true,
    processEnvironments: true,
    tags: "ams",
    macros: {
      rr: "\\mathbb{R}",
      nn: "\\mathbb{N}",
      zz: "\\mathbb{Z}",
      cc: "\\mathbb{C}",
      pp: "\\mathbb{P}",
      dd: "\\mathrm{d}",
      dv: "\\mathcal{D}",
      klein: "\\mathcal{K}",
      spinor: "\\mathcal{S}",
    },
  },
  options: {
    ignoreHtmlClass: /(^|\\s)no-math(\\s|$)/,
  },
  chtml: {
    scale: 1.0,
    minScale: 0.5,
    matchFontDimensions: false,
  },
};

document$.subscribe(() => {
  MathJax.typesetPromise();
});
