import * as hglib from "https://esm.sh/higlass@1.13?deps=react@17,react-dom@17,pixi.js@6";

/**
 * @param {{
 *   xDomain: [number, number],
 *   yDomain: [number, number],
 * }} location
 */
function toPts({ xDomain, yDomain }) {
  let [x, xe] = xDomain;
  let [y, ye] = yDomain;
  return [x, xe, y, ye];
}

/**
 * @param {HTMLElement} el
 * @returns {() => void} unlisten
 */
function addEventListenersTo(el) {
  let controller = new AbortController();

  // prevent right click events from bubbling up to Jupyter/JupyterLab
  el.addEventListener("contextmenu", (event) => event.stopPropagation(), {
    signal: controller.signal,
  });

  return () => controller.abort();
}

/** @type {import("npm:@anywidget/types@0.2.0").Render} */
async function render({ model, el }) {
  let viewconf = model.get("_viewconf");
  let options = model.get("_options") ?? {};
  let api = await hglib.viewer(el, viewconf, options);
  let unlisten = addEventListenersTo(el);

  model.on("msg:custom", (msg) => {
    msg = JSON.parse(msg);
    let [fn, ...args] = msg;
    api[fn](...args);
  });

  if (viewconf.views.length === 1) {
    api.on("location", (loc) => {
      model.set("location", toPts(loc));
      model.save_changes();
    }, viewconf.views[0].uid);
  } else {
    viewconf.views.forEach((view, idx) => {
      api.on("location", (loc) => {
        let copy = model.get("location").slice();
        copy[idx] = toPts(loc);
        model.set("location", copy);
        model.save_changes();
      }, view.uid);
    });
  }
  return () => {
    unlisten();
  };
}

export default { render };
