/**
 * 通用工具函数
 */

/**
 * 格式化日期时间为 YYYY-MM-DD HH:mm:ss
 * @param {Date} date 
 * @returns {string}
 */
function formatDateTime(date) {
  const pad = (n) => String(n).padStart(2, '0');
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`;
}

module.exports = {
  formatDateTime
};
