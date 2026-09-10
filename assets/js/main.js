// Patricia Luber – Malerei | Nachbau der Wix-Seite
// Mobile-Navigation + Produkt-Slider (Startseite) + Kontaktformular (mailto, mit Betreff-Vorbelegung per URL)

document.addEventListener('DOMContentLoaded', function () {
  // Mobile nav toggle
  var toggle = document.getElementById('navToggle');
  var nav = document.getElementById('siteNav');
  if (toggle && nav) {
    toggle.addEventListener('click', function () {
      var isOpen = nav.classList.toggle('open');
      toggle.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
    });
  }

  // Ausklapp-Menü "Öl & Acryl" (per Tap auf Mobilgeräten; auf dem Desktop reicht Hover)
  var hasSub = document.querySelector('.has-sub');
  var subToggle = document.querySelector('.sub-toggle');
  if (hasSub && subToggle) {
    subToggle.addEventListener('click', function (e) {
      e.preventDefault();
      var isOpen = hasSub.classList.toggle('sub-open');
      subToggle.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
    });
    // Außerhalb des Menüs tippen/klicken schließt das Untermenü wieder
    document.addEventListener('click', function (e) {
      if (hasSub.classList.contains('sub-open') && !hasSub.contains(e.target)) {
        hasSub.classList.remove('sub-open');
        subToggle.setAttribute('aria-expanded', 'false');
      }
    });
    // Beim Schließen des Hauptmenüs auch das Untermenü zurücksetzen
    if (toggle) {
      toggle.addEventListener('click', function () {
        if (!nav.classList.contains('open')) {
          hasSub.classList.remove('sub-open');
          subToggle.setAttribute('aria-expanded', 'false');
        }
      });
    }
  }

  // Produkt-Slider (Startseite)
  var slider = document.getElementById('productSlider');
  var prevBtn = document.querySelector('.slider-prev');
  var nextBtn = document.querySelector('.slider-next');
  if (slider && prevBtn && nextBtn) {
    var stepSize = function () {
      var card = slider.querySelector('.slider-card');
      var gap = 19; // entspricht 1.2rem Abstand im CSS
      var cardWidth = card ? card.getBoundingClientRect().width : 240;
      return (cardWidth + gap) * 2;
    };
    prevBtn.addEventListener('click', function () {
      slider.scrollBy({ left: -stepSize(), behavior: 'smooth' });
    });
    nextBtn.addEventListener('click', function () {
      slider.scrollBy({ left: stepSize(), behavior: 'smooth' });
    });
  }

  // Slider-Punkte: zeigen, wie viele "Seiten" es gibt und wie weit man klicken kann
  var sliderDots = document.getElementById('sliderDots');
  if (slider && sliderDots) {
    var dotButtons = [];
    var updateActiveDot = function () {
      if (!dotButtons.length) { return; }
      var pageWidth = slider.clientWidth || 1;
      var active = Math.round(slider.scrollLeft / pageWidth);
      active = Math.max(0, Math.min(dotButtons.length - 1, active));
      dotButtons.forEach(function (dot, i) {
        dot.classList.toggle('active', i === active);
      });
    };
    var buildDots = function () {
      var pageWidth = slider.clientWidth;
      var pages = pageWidth > 0 ? Math.round(slider.scrollWidth / pageWidth) : 1;
      pages = Math.max(1, pages);
      sliderDots.innerHTML = '';
      dotButtons = [];
      if (pages <= 1) {
        sliderDots.hidden = true;
        return;
      }
      sliderDots.hidden = false;
      for (var i = 0; i < pages; i++) {
        var dot = document.createElement('button');
        dot.type = 'button';
        dot.className = 'slider-dot';
        dot.setAttribute('aria-label', 'Zu Bildern ' + (i + 1) + ' von ' + pages + ' springen');
        (function (index) {
          dot.addEventListener('click', function () {
            slider.scrollTo({ left: index * slider.clientWidth, behavior: 'smooth' });
          });
        })(i);
        sliderDots.appendChild(dot);
        dotButtons.push(dot);
      }
      updateActiveDot();
    };
    var scrollTick = false;
    slider.addEventListener('scroll', function () {
      if (scrollTick) { return; }
      scrollTick = true;
      window.requestAnimationFrame(function () {
        updateActiveDot();
        scrollTick = false;
      });
    });
    var resizeTimer;
    window.addEventListener('resize', function () {
      window.clearTimeout(resizeTimer);
      resizeTimer = window.setTimeout(buildDots, 150);
    });
    window.addEventListener('load', buildDots);
    buildDots();
  }

  // Contact form -> mailto
  var form = document.getElementById('contactForm');
  if (form) {
    var pageLang = (document.documentElement.lang || 'de').toLowerCase().indexOf('en') === 0 ? 'en' : 'de';
    // Betreff aus URL-Parameter vorbelegen (z.B. von einer Werk-Seite verlinkt)
    var params = new URLSearchParams(window.location.search);
    var prefillSubject = params.get('subject');
    var subjectField = document.getElementById('subject');
    var messageField = document.getElementById('message');
    if (prefillSubject && subjectField) {
      subjectField.value = prefillSubject;
      if (messageField && !messageField.value) {
        messageField.value = pageLang === 'en'
          ? 'Hello Ms. Luber,\n\nI have the following question: '
          : 'Hallo Frau Luber,\n\nich habe folgende Frage: ';
      }
    }

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var name = document.getElementById('name').value.trim();
      var email = document.getElementById('email').value.trim();
      var subject = document.getElementById('subject').value.trim() || (pageLang === 'en' ? 'Contact request via website' : 'Kontaktanfrage über die Website');
      var message = document.getElementById('message').value.trim();

      var body = 'Name: ' + name + '\n' + 'Email: ' + email + '\n\n' + message;
      var mailto = 'mailto:luber.laporte@web.de' +
        '?subject=' + encodeURIComponent(subject) +
        '&body=' + encodeURIComponent(body);

      var status = document.getElementById('formStatus');
      if (status) {
        status.hidden = false;
      }
      window.location.href = mailto;
    });
  }

  // Product image gallery: click a thumbnail to swap the main image
  var mainImg = document.getElementById('gallery-main-img');
  var thumbs = document.querySelectorAll('.thumb');
  if (mainImg && thumbs.length) {
    thumbs.forEach(function (thumb) {
      thumb.addEventListener('click', function () {
        var src = thumb.getAttribute('data-src');
        if (src) {
          mainImg.setAttribute('src', src);
        }
        thumbs.forEach(function (t) { t.classList.remove('active'); });
        thumb.classList.add('active');
      });
    });
  }

  // Category page: "Sortieren nach" dropdown to sort the product grid
  var sortSelect = document.getElementById('sortSelect');
  var artGrid = document.getElementById('artGrid');
  if (sortSelect && artGrid) {
    sortSelect.addEventListener('change', function () {
      var cards = Array.prototype.slice.call(artGrid.children);
      var mode = sortSelect.value;
      if (mode === 'name-asc') {
        cards.sort(function (a, b) { return a.dataset.name.localeCompare(b.dataset.name, 'de'); });
      } else if (mode === 'name-desc') {
        cards.sort(function (a, b) { return b.dataset.name.localeCompare(a.dataset.name, 'de'); });
      } else {
        cards.sort(function (a, b) { return a.dataset.order - b.dataset.order; });
      }
      cards.forEach(function (card) { artGrid.appendChild(card); });
    });
  }
});
