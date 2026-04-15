(function () {
  var LANGUAGES = [
    { code: 'en', name: 'English',       indexFile: 'index.html',    privacyFile: 'privacy.html' },
    { code: 'ar', name: 'العربية',       indexFile: 'index-ar.html', privacyFile: 'privacy-ar.html' },
    { code: 'de', name: 'Deutsch',       indexFile: 'index-de.html', privacyFile: 'privacy-de.html' },
    { code: 'es', name: 'Español',       indexFile: 'index-es.html', privacyFile: 'privacy-es.html' },
    { code: 'fi', name: 'Suomi',         indexFile: 'index-fi.html', privacyFile: 'privacy-fi.html' },
    { code: 'fr', name: 'Français',      indexFile: 'index-fr.html', privacyFile: 'privacy-fr.html' },
    { code: 'ms', name: 'Bahasa Melayu', indexFile: 'index-ms.html', privacyFile: 'privacy-ms.html' },
    { code: 'no', name: 'Norsk',         indexFile: 'index-no.html', privacyFile: 'privacy-no.html' },
    { code: 'sv', name: 'Svenska',       indexFile: 'index-sv.html', privacyFile: 'privacy-sv.html' },
    { code: 'th', name: 'ไทย',           indexFile: 'index-th.html', privacyFile: 'privacy-th.html' },
    { code: 'tr', name: 'Türkçe',        indexFile: 'index-tr.html', privacyFile: 'privacy-tr.html' },
    { code: 'zh', name: '中文',           indexFile: 'index-zh.html', privacyFile: 'privacy-zh.html' },
  ];

  function getPageInfo() {
    var filename = window.location.pathname.split('/').pop() || 'index.html';

    if (filename.indexOf('privacy') === 0) {
      var pm = filename.match(/^privacy-([a-z]+)\.html$/);
      return { type: 'privacy', lang: pm ? pm[1] : 'en' };
    }

    if (filename === 'index.html' || filename === '') {
      return { type: 'index', lang: 'en' };
    }

    var im = filename.match(/^index-([a-z]+)\.html$/);
    if (im) return { type: 'index', lang: im[1] };

    return { type: 'other', lang: 'en' };
  }

  function initLangSelector() {
    var header = document.querySelector('header');
    if (!header) return;

    var pageInfo = getPageInfo();
    var currentLang = pageInfo.lang;

    var selector = document.createElement('div');
    selector.className = 'lang-selector';

    var optionsHTML = LANGUAGES.map(function (lang) {
      var isActive = lang.code === currentLang;
      var targetFile = pageInfo.type === 'privacy' ? lang.privacyFile : lang.indexFile;
      return (
        '<a href="' + targetFile + '" class="lang-option' + (isActive ? ' active' : '') + '" data-lang="' + lang.code + '">' +
          '<span class="lang-option-name">' + lang.name + '</span>' +
          '<span class="lang-option-code">' + lang.code.toUpperCase() + '</span>' +
        '</a>'
      );
    }).join('');

    selector.innerHTML =
      '<button class="lang-btn" aria-label="Select language" aria-expanded="false">' +
        '<span class="lang-globe">&#127760;</span>' +
        '<span class="lang-current">' + currentLang.toUpperCase() + '</span>' +
        '<span class="lang-caret">&#9662;</span>' +
      '</button>' +
      '<div class="lang-dropdown" role="listbox">' + optionsHTML + '</div>';

    header.appendChild(selector);

    var btn = selector.querySelector('.lang-btn');

    btn.addEventListener('click', function (e) {
      e.stopPropagation();
      var isOpen = selector.classList.toggle('open');
      btn.setAttribute('aria-expanded', String(isOpen));
    });

    document.addEventListener('click', function () {
      selector.classList.remove('open');
      btn.setAttribute('aria-expanded', 'false');
    });

    selector.addEventListener('click', function (e) {
      e.stopPropagation();
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initLangSelector);
  } else {
    initLangSelector();
  }
})();
