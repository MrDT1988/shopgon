/* Shop Gọn — HIỆU ỨNG THEO MÙA (dùng chung: app, trang Thiết kế hình, robot hàng chờ).
 * 29/10/2026 anh Thái: hiệu ứng tự đổi theo ngày. Làm Noel tuyết rơi trước; mùa khác có tên, hiệu ứng làm dần.
 * muaHienTai(date?) → {id, ten, nhan, tu, den, co} | null   (co = đã có hiệu ứng vẽ) */
(function (g) {
  /* Tết âm lịch + Trung thu (rằm tháng 8) — ngày dương */
  var TET = { 2027: '2027-02-06', 2028: '2028-01-26', 2029: '2029-02-13', 2030: '2030-02-03', 2031: '2031-01-23' };
  var TRUNGTHU = { 2027: '2027-09-15', 2028: '2028-10-03', 2029: '2029-09-22', 2030: '2030-09-12', 2031: '2031-10-01' };
  function ymd(d) { return d.getFullYear() * 10000 + (d.getMonth() + 1) * 100 + d.getDate(); }
  function cong(s, n) { var p = s.split('-'), d = new Date(+p[0], +p[1] - 1, +p[2] + n); return ymd(d); }
  function blackFriday(y) { var d = new Date(y, 10, 1), dem = 0; while (true) { if (d.getDay() === 5 && ++dem === 4) return d; d.setDate(d.getDate() + 1); } }
  function ds(y) {
    var bf = blackFriday(y), bfs = y + '-11-' + String(bf.getDate()).padStart(2, '0');
    var L = [
      { id: 'phunu2010', ten: 'Phụ nữ Việt Nam 20/10', nhan: '🌷 20/10', a: y * 10000 + 1015, b: y * 10000 + 1020, co: 0 },
      { id: 'nhagiao', ten: 'Nhà giáo 20/11', nhan: '📚 20/11', a: y * 10000 + 1113, b: y * 10000 + 1120, co: 0 },
      { id: 'blackfriday', ten: 'Black Friday', nhan: '🖤 Black Friday', a: cong(bfs, -6), b: cong(bfs, 3), co: 0 },
      { id: 'noel', ten: 'Giáng sinh — tuyết rơi', nhan: '🎄 Noel', a: y * 10000 + 1201, b: y * 10000 + 1225, co: 1 },
      { id: 'namoi', ten: 'Năm mới — pháo hoa', nhan: '🎆 Năm mới', a: y * 10000 + 1226, b: (y + 1) * 10000 + 101, co: 0 },
      { id: 'phunu83', ten: 'Quốc tế Phụ nữ 8/3', nhan: '🌹 8/3', a: y * 10000 + 301, b: y * 10000 + 308, co: 0 },
      { id: 'le304', ten: 'Lễ 30/4 – 1/5', nhan: '🇻🇳 30/4', a: y * 10000 + 425, b: y * 10000 + 501, co: 0 }
    ];
    if (TET[y]) L.push({ id: 'tet', ten: 'Tết — mai đào', nhan: '🧧 Tết', a: cong(TET[y], -20), b: cong(TET[y], 6), co: 0 });
    if (TRUNGTHU[y]) L.push({ id: 'trungthu', ten: 'Trung thu', nhan: '🏮 Trung thu', a: cong(TRUNGTHU[y], -10), b: TRUNGTHU[y].replace(/-/g, '') * 1, co: 0 });
    return L;
  }
  function muaHienTai(d) {
    d = d || new Date(); var n = ymd(d), y = d.getFullYear();
    var L = ds(y).concat(ds(y - 1));
    for (var i = 0; i < L.length; i++) if (n >= L[i].a && n <= L[i].b) { var m = L[i]; return { id: m.id, ten: m.ten, nhan: m.nhan, tu: m.a, den: m.b, co: !!m.co }; }
    return null;
  }
  function muaSap(d) { /* mùa kế tiếp (để app báo trước) */
    d = d || new Date(); var n = ymd(d), y = d.getFullYear(), L = ds(y).concat(ds(y + 1)).filter(function (m) { return m.a > n; }).sort(function (a, b) { return a.a - b.a; });
    return L[0] ? { id: L[0].id, ten: L[0].ten, nhan: L[0].nhan, tu: L[0].a, co: !!L[0].co } : null;
  }
  g.muaHienTai = muaHienTai; g.muaSap = muaSap;
  g.MUA_IDS = ['noel', 'namoi', 'tet', 'blackfriday', 'nhagiao', 'phunu2010', 'phunu83', 'le304', 'trungthu'];
})(typeof window !== 'undefined' ? window : globalThis);
