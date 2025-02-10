import * as hglib from "https://esm.sh/higlass@1.13?deps=react@17,react-dom@17,pixi.js@6";
import { v4 } from "https://esm.sh/@lukeed/uuid@2.0.1";

/** @import { HGC, PluginDataFetcherConstructor } from "./types.ts" */

// Make sure plugins are registered and enabled
window.higlassDataFetchersByType = window.higlassDataFetchersByType ||
  {};

/**
 * Create a unique identifier.
 * @returns {string}
 */
function uid() {
  return v4().split("-")[0];
}

/**
 * Make an assertion.
 *
 * @param {unknown} expression - The expression to test.
 * @param {string=} msg - The optional message to display if the assertion fails.
 * @returns {asserts expression}
 * @throws an {@link Error} if `expression` is not truthy.
 */
function assert(expression, msg = "") {
  if (!expression) throw new Error(msg);
}

/**
 * Send a custom message to Python and _await_ a response.
 *
 * Unlike typical "fire-and-forget" messages, this function returns a `Promise`
 * that resolves when a response is received back from Python.
 *
 * A message is sent with a unique `id` and a payload. The Python handler should:
 *
 * 1. Process the message.
 * 2. Respond with the same `id` and a new payload.
 *
 * An `AbortSignal` can be used to adjust whether the promise should reject (default: a 3s timeout).
 *
 * **Example:**
 *
 * ```js
 * let response = await sendCustomMessage(model, { payload: "hello" });
 * console.log(response.payload); // HELLO
 * ```
 *
 * **Python handler:**
 *
 * ```py
 * widget = Widget()
 * widget.on_msg(lambda msg, buffers: widget.send({
 *     "id": msg["id"], "payload": msg["payload"].upper()
 * }))
 * ```
 *
 * @template T
 * @param {import("npm:@anywidget/types").AnyModel} model
 * @param {{ payload: unknown, signal?: AbortSignal, buffers?: Array<ArrayBuffer> }} options
 * @return {Promise<{ payload: T, buffers: Array<DataView> }>}
 */
function sendCustomMessage(model, options) {
  let id = uid();
  let signal = options.signal ?? AbortSignal.timeout(3000);

  return new Promise((resolve, reject) => {
    if (signal.aborted) {
      reject(signal.reason);
    }

    signal.addEventListener("abort", () => {
      model.off("msg:custom", handler);
      reject(signal.reason);
    });

    /**
     * @param {{ id: string, payload: T }} msg
     * @param {DataView[]} buffers
     */
    function handler(msg, buffers) {
      if (!(msg.id === id)) return;
      resolve({ payload: msg.payload, buffers });
      model.off("msg:custom", handler);
    }

    model.on("msg:custom", handler);
    model.send(
      { id, payload: options.payload },
      undefined,
      options.buffers ?? [],
    );
  });
}

/**
 * Transforms the original view config into tracks recognized by the custom data fetcher.
 *
 * Finds tracks with `server: 'jupyter'`, removes the key, and adds a `data` object
 * with `type: dataFetcherId` and the track’s `tilesetUid`.
 *
 * @param {Record<string, unknown>} viewConfig - The original view configuration.
 * @param {string} dataFetcherId - The identifier for Jupyter-based data sources.
 * @returns {Record<string, unknown>} A modified deep copy of the view config.
 *
 * @example
 * ```js
 * resolveJupyterServers(
 *   { views: [{ tracks: { top: [{ server: 'jupyter', tilesetUid: 'abc' }] } }] },
 *   'jupyter-123'
 * );
 * // Returns:
 * // {
 * //   views: [{ tracks: { top: [{ tilesetUid: 'abc', data: { type: 'jupyter-123', tilesetUid: 'abc' } }] } }]
 * // }
 * ```
 */
function resolveJupyterServers(viewConfig, dataFetcherId) {
  let copy = JSON.parse(JSON.stringify(viewConfig));
  for (let view of copy.views) {
    for (let track of Object.values(view.tracks).flat()) {
      if (track?.server === "jupyter") {
        delete track.server;
        track.data = track.data || {};
        track.data.type = dataFetcherId;
        track.data.tilesetUid = track.tilesetUid;
      }
    }
  }
  return copy;
}

/**
 * @param {import("npm:@anywidget/types").AnyModel} model
 * @returns{PluginDataFetcherConstructor}
 */
function createDataFetcherForModel(model) {
  /**
   * @param {HGC} hgc
   * @param {Record<string, unknown>} dataConfig
   * @param {unknown} pubSub
   */
  const DataFetcher = function createDataFetcher(hgc, dataConfig, pubSub) {
    let config = { ...dataConfig, server: "jupyter" };
    return new hgc.dataFetchers.DataFetcher(config, pubSub, {
      async fetchTiles({ tileIds }) {
        let response = await sendCustomMessage(model, {
          payload: { type: "tiles", tileIds },
        });
        let result = hgc.services.tileResponseToData(
          response.payload,
          "jupyter",
          tileIds,
        );
        return result;
      },
      async fetchTilesetInfo({ server, tilesetUid }) {
        assert(server === "jupyter", "must be a jupyter server");
        let response = await sendCustomMessage(model, {
          payload: { type: "tileset_info", tilesetUid },
        });
        return response.payload;
      },
      registerTileset() {
        throw new Error("Not implemented");
      },
    });
  };

  return /** @type{any} */ (DataFetcher);
}

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

export default () => {
  let id = `jupyter-${uid()}`;
  return {
    /** @type{import("npm:@anywidget/types@0.2.0").Initialize<{ _ts: string }>} */
    async initialize({ model }) {
      let tsId = model.get("_ts");
      let tsModel = await model.widget_manager.get_model(
        tsId.slice("IPY_MODEL_".length),
      );
      window.higlassDataFetchersByType[tsId] = {
        name: id,
        dataFetcher: createDataFetcherForModel(tsModel),
      };
    },
    /** @type{import("npm:@anywidget/types@0.2.0").Render} */
    async render({ model, el }) {
      /** @type {{ views: Array<{ uid: string }> }} */
      let viewconf = model.get("_viewconf");
      let options = model.get("_options") ?? {};
      let resolved = resolveJupyterServers(viewconf, model.get("_ts"));
      let api = await hglib.viewer(el, resolved, options);

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
    },
  };
};
