/**
 * India Universal Geocompute Engine - Zero-Dependency JS SDK
 * Works directly in Browser, React, React Native, Node.js, and Bun.
 */
class IndiaGeoEngine {
  constructor(cdnBase = "https://cdn.jsdelivr.net/gh/<owner>/<repo>@main/api/v1") {
    this.cdnBase = cdnBase;
    this.cache = new Map();
  }

  async getNationalIndex() {
    const res = await fetch(`${this.cdnBase}/india.json`);
    return res.json();
  }

  async getStateDossier(stateSlug) {
    const res = await fetch(`${this.cdnBase}/states/${stateSlug}.json`);
    return res.json();
  }

  async getDistrictPackage(stateSlug, districtSlug) {
    const key = `${stateSlug}:${districtSlug}`;
    if (this.cache.has(key)) return this.cache.get(key);

    const res = await fetch(`${this.cdnBase}/districts/${stateSlug}/${districtSlug}.json`);
    const data = await res.json();
    this.cache.set(key, data);
    return data;
  }

  async findVillage(stateSlug, districtSlug, query) {
    const pkg = await this.getDistrictPackage(stateSlug, districtSlug);
    const q = query.toLowerCase().trim();
    return pkg.villages.find(v => v.name.toLowerCase() === q || String(v.id) === q);
  }
}

if (typeof module !== 'undefined') module.exports = IndiaGeoEngine;
