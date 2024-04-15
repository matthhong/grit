export default class Tooltip {
  constructor(selection) {
    if (!selection || !selection.size()) {
      throw "Requires a tooltip div element selection";
    }
    this._selection = selection;
  }

  move(event) {
    const margin = 20;
    const { clientX: x, clientY: y } = event;
    
    const { width, height } = this.selection.node().getBoundingClientRect();
    const left = this.clamp(
      margin,
      x - width / 2,
      window.innerWidth - width - margin
    );
    const top =
      window.innerHeight > y + margin + height
        ? y + margin
        : y - height - margin;
    this.selection.style("top", `${top}px`).style("left", `${left}px`);
  }

  display(datum, callback) {
    if (!callback || typeof callback !== "function") {
      throw "ToolTip.display requires a callback function that returns an HTML string";
    }
    this.selection.style("display", "block").html(callback(datum));
  }

  hide() {
    this.selection.style("display", "none").html("");
  }

  clamp(min, d, max) {
    return Math.max(min, Math.min(max, d));
  }

  get selection() {
    return this._selection;
  }

  set selection(sel) {
    if (sel && sel.size()) {
      this._selection = sel;
    } else {
      throw "selection must be a non-empty selected element";
    }
  }
}