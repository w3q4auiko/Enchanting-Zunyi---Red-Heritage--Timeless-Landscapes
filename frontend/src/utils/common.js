/**
 * 前端通用工具函数模块。
 *
 * 用于统一资源路径处理与交互手势行为，形成可复用的 UI 基础能力，
 * 支撑旅游信息系统前台的统一体验规范。
 */

/**
 * 规范化资源 URL，统一斜杠方向以适配静态资源路径。
 *
 * @param {string} url - 原始路径。
 * @returns {string} 规范化后的路径。
 */
export const fixUrl = (url) => {
  if (typeof url !== "string" || !url) return "";
  return url.replace(/\\/g, "/");
};

/**
 * 为横向内容容器注入拖拽滚动交互。
 *
 * 该能力用于横向资源卡片的浏览体验，增强游客在景区、美食等列表
 * 页面中的连续探索效率。
 *
 * @param {HTMLElement} slider - 承载横向滚动的容器元素。
 * @returns {(() => void) | undefined} 清理函数，若初始化失败则返回 undefined。
 */
export const applyDragScroll = (slider) => {
  if (!slider || !(slider instanceof HTMLElement)) return;
  if (slider.dataset.dragInitialized === "true") return;
  slider.dataset.dragInitialized = "true";

  let isDown = false;
  let startX = 0;
  let scrollLeft = 0;
  let isDragging = false;

  /**
   * 记录拖拽起始点。
   * @param {MouseEvent} e - 鼠标按下事件。
   * @returns {void}
   */
  const onMouseDown = (e) => {
    isDown = true;
    isDragging = false;
    slider.classList.add("active");
    startX = e.pageX - slider.offsetLeft;
    scrollLeft = slider.scrollLeft;
  };

  /**
   * 结束拖拽并恢复视觉状态。
   * @returns {void}
   */
  const onMouseLeave = () => {
    isDown = false;
    slider.classList.remove("active");
  };

  /**
   * 结束拖拽并恢复视觉状态。
   * @returns {void}
   */
  const onMouseUp = () => {
    isDown = false;
    slider.classList.remove("active");
  };

  /**
   * 执行拖拽位移计算并更新滚动位置。
   * @param {MouseEvent} e - 鼠标移动事件。
   * @returns {void}
   */
  const onMouseMove = (e) => {
    if (!isDown) return;

    e.preventDefault();

    const x = e.pageX - slider.offsetLeft;
    const walk = (x - startX) * 2;

    if (Math.abs(walk) > 5) {
      isDragging = true;
    }

    slider.scrollLeft = scrollLeft - walk;
  };

  /**
   * 防止拖拽状态下触发点击。
   * @param {MouseEvent} e - 点击事件。
   * @returns {void}
   */
  const onClick = (e) => {
    if (isDragging) {
      e.preventDefault();
      e.stopPropagation();
      isDragging = false;
    }
  };

  slider.addEventListener("mousedown", onMouseDown);
  slider.addEventListener("mouseleave", onMouseLeave);
  slider.addEventListener("mouseup", onMouseUp);
  slider.addEventListener("mousemove", onMouseMove);
  slider.addEventListener("click", onClick, true);

  return () => {
    slider.removeEventListener("mousedown", onMouseDown);
    slider.removeEventListener("mouseleave", onMouseLeave);
    slider.removeEventListener("mouseup", onMouseUp);
    slider.removeEventListener("mousemove", onMouseMove);
    slider.removeEventListener("click", onClick, true);
    delete slider.dataset.dragInitialized;
  };
};
