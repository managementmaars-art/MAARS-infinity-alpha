import { decode } from 'he';

export default class Dictionary {
  constructor() {
    this.translation = {};
  }

  fill(translation = {}) {
    this.translation = this.sanitize(translation);
  }

  get(key, base = this.translation) {
    const splits = key.split(/[./]+/);

    if (splits.length === 1) {
      return base[key];
    }

    key = splits.shift();

    if (typeof base[key] !== 'object') {
      return;
    }

    return this.get(splits.join('.'), base[key]);
  }

  sanitize(translation) {
    if (typeof translation === 'object') {
      for (let key in translation) {
        translation[key] = this.sanitize(translation[key]);
      }
    }
    else if (typeof translation === 'string') {
      translation = decode(translation);
      const div = document.createElement('div');
      div.innerHTML = translation;
      translation = div.textContent || div.innerText || '';
    }
    else {
      // Invalid translation
    }

    return translation;
  }
}
