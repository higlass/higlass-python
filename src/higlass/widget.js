<<<<<<< HEAD
import * as hglib from "https://esm.sh/higlass@2.2.3?deps=react@17,react-dom@17,pixi.js@6";
=======
import * as hglib from "https://esm.sh/higlass@2.2.1?deps=react@17,react-dom@17,pixi.js@6";
>>>>>>> 59fdefa (Bumped higlass version)
import { v4 } from "https://esm.sh/@lukeed/uuid@2.0.1";

/** @import { AnyModel } from "@anywidget/types" */
/** @import { PluginDataFetcherConstructor, GenomicLocation, Viewconf, DataFetcher} from "./types.ts" */

const NAME = "jupyter";

let HIGLASS_STYLES = new CSSStyleSheet();
HIGLASS_STYLES.replaceSync(hglib.CSS);

/**
 * @param {string} href
 * @returns {Promise<void>}
 */
function loadScript(href) {
  /** @param {string} href */
  function isScriptLoaded(href) {
    return document.querySelector(`script[src="${href}"]`) !== null;
  }

  return new Promise((resolve, reject) => {
    if (isScriptLoaded(href)) {
      return resolve();
    }
    let script = document.createElement("script");
    script.src = href;
    script.async = true;
    script.onload = () => resolve();
    script.onerror = () => reject(new Error(`Failed to load ${href}`));
    document.head.appendChild(script);
  });
}

/**
 * Temporarily disables RequireJS to reliably load legacy scripts, then restores it.
 *
 * Clears `window.require`, `window.requirejs`, and `window.define` to prevent
 * interference from RequireJS when loading scripts.
 *
 * @param {Array<string>} pluginUrls - URLs of the scripts to load.
 * @returns {Promise<void>} Resolves when all scripts have been processed.
 */
async function requireScripts(pluginUrls) {
  let backup = {
    // @ts-expect-error - not on the window
    define: window.define,
    require: window.require,
    // @ts-expect-error - not on the window
    requirejs: window.requirejs,
  };
  for (let field of Object.keys(backup)) {
    // @ts-expect-error - not on the window
    window[field] = undefined;
  }

  let results = await Promise.allSettled(pluginUrls.map(loadScript));

  results.forEach((result, i) => {
    if (result.status === "rejected") {
      console.warn(`Failed to load script: ${pluginUrls[i]}`, result.reason);
    }
  });

  Object.assign(window, backup);
}

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
 * @param {AnyModel} model
 * @param {{ payload: unknown, signal?: AbortSignal }} options
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
    model.send({ id, payload: options.payload });
  });
}

/**
 * Transforms the original view config into tracks recognized by the custom data fetcher.
 *
 * Finds tracks with `server: 'jupyter'`, removes the key, and adds a `data` object
 * with `type: dataFetcherId` and the track’s `tilesetUid`.
 *
 * @param {Viewconf} viewConfig - The original view configuration.
 * @returns {Viewconf} A modified deep copy of the view config.
 *
 * @example
 * ```js
 * resolveJupyterServers(
 *   { views: [{ tracks: { top: [{ server: 'jupyter', tilesetUid: 'abc' }] } }] },
 *   'jupyter-123'
 * );
 * // Returns:
 * // {
 * //   views: [{ tracks: { top: [{ tilesetUid: 'abc', data: { type: 'jupyter', tilesetUid: 'abc' } }] } }]
 * // }
 * ```
 */
function resolveJupyterServers(viewConfig) {
  const copy = JSON.parse(JSON.stringify(viewConfig));

  for (const view of copy.views) {
    const baseTracks = Object.values(view.tracks).flat();
    let allTracks = Object.values(view.tracks).flat();

    for (const track of baseTracks) {
      // Go through and check for combined tracks
      if (track.contents) {
        allTracks = allTracks.concat(allTracks, track.contents);
      }
    }

    for (const track of allTracks) {
      if (track?.server === NAME) {
        delete track.server;
        track.data = track.data || {};
        track.data.type = NAME;
        track.data.tilesetUid = track.tilesetUid;
      }
    }
  }
  return copy;
}

/**
 * @param {AnyModel<State>} model */
async function registerJupyterHiGlassDataFetcher(model) {
  if (window?.higlassDataFetchersByType?.[NAME]) {
    return;
  }

  let tModel = await model.widget_manager.get_model(
    model.get("_tileset_client").slice("IPY_MODEL_".length),
  );

  /** @type {(...args: ConstructorParameters<PluginDataFetcherConstructor>) => DataFetcher} */
  function DataFetcher(hgc, dataConfig, pubSub) {
    let config = { ...dataConfig, server: NAME };

    return new hgc.dataFetchers.DataFetcher(config, pubSub, {
      async fetchTilesetInfo({ server, tilesetUid }) {
        assert(server === NAME, "must be a jupyter server");
        let response = await sendCustomMessage(tModel, {
          payload: { type: "tileset_info", tilesetUid },
        });
        return response.payload;
      },
      fetchTiles: consolidator(
        /** @param {Array<WithResolvers<{ tileIds: Array<string> }, Record<string, any>>>} requests */
        async (requests) => {
          let tileIds = [...new Set(requests.flatMap((r) => r.data.tileIds))];
          let response = await sendCustomMessage(tModel, {
            payload: { type: "tiles", tileIds },
          });
          let tiles = hgc.services.tileResponseToData(
            response.payload,
            NAME,
            tileIds,
          );
          for (let request of requests) {
            /** @type {Record<string, unknown>} */
            const requestData = {};
            for (let id of request.data.tileIds) {
              let tileData = tiles[id];
              if (tileData) requestData[id] = tileData;
            }
            request.resolve(requestData);
          }
        },
      ),
      registerTileset() {
        throw new Error("Not implemented");
      },
    });
  }

  /** @type {PluginDataFetcherConstructor} */
  // @ts-expect-error - classic function definition (above) supports `new` invocation
  let dataFetcher = DataFetcher;

  window.higlassDataFetchersByType ??= {};
  window.higlassDataFetchersByType[NAME] = { name: NAME, dataFetcher };
}

/**
 * @param {GenomicLocation} location
 * @returns {[number, number, number, number]}
 */
function locationToCoordinates({ xDomain, yDomain }) {
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

  // prevent wheel events from scrolling the page while allowing HiGlass zoom
  el.addEventListener("wheel", (event) => {
    event.preventDefault();
    event.stopPropagation();
  }, {
    signal: controller.signal,
    passive: false,
  });

  return () => controller.abort();
}

/**
 * @typedef State
 * @property {Viewconf} _viewconf
 * @property {Record<string, unknown>} _options
 * @property {`IPY_MODEL_${string}`} _tileset_client
 * @property {Array<number> | Array<Array<number>>} location
 * @property {Array<string>} _plugin_urls
 */

export default {
  /** @type {import("@anywidget/types").Render<State>} */
  async render({ model, el }) {
    await Promise.all([
      requireScripts(model.get("_plugin_urls")),
      registerJupyterHiGlassDataFetcher(model),
    ]);
    let viewconf = resolveJupyterServers(
      model.get("_viewconf"),
    );
    let options = model.get("_options") ?? {};

    let shadow = el.shadowRoot ?? el.attachShadow({ mode: "open" });
    shadow.innerHTML = "";
    shadow.adoptedStyleSheets = [HIGLASS_STYLES];
    let container = document.createElement("div");
    shadow.appendChild(container);

    let api = await hglib.viewer(container, viewconf, options);
    let unlisten = addEventListenersTo(el);

    model.on("msg:custom", (msg) => {
      msg = JSON.parse(msg);
      let [fn, ...args] = msg;
      /** @type {any} */ (api)[fn](...args);
    });

    if (viewconf.views.length === 1) {
      api.on(
        "location",
        (/** @type {GenomicLocation} */ loc) => {
          model.set("location", locationToCoordinates(loc));
          model.save_changes();
        },
        viewconf.views[0].uid,
        undefined,
      );
    } else {
      viewconf.views.forEach((view, idx) => {
        api.on(
          "location",
          (/** @type{GenomicLocation} */ loc) => {
            let location = model.get("location").slice();
            location[idx] = locationToCoordinates(loc);
            model.set("location", location);
            model.save_changes();
          },
          view.uid,
          undefined,
        );
      });
    }

    return () => {
      unlisten();
    };
  },
};

/**
 * @template T
 * @template U
 * @typedef {{ data: T, resolve: (success: U) => void, reject: (err: unknown) => void }} WithResolvers
 */

/**
 * Collects multiple calls within the same frame to processes them as a batch.
 *
 * The provided `processBatch` function receives an array of items, each with
 * associated resolvers for fulfilling the original request.
 *
 * @template T
 * @template U
 * @param {(batch: Array<WithResolvers<T, U>>) => void} processBatch - A function to process each batch.
 * @returns {(item: T) => Promise<U>} - A function to enqueue items.
 */
function consolidator(processBatch) {
  /** @type {Array<WithResolvers<T, U>>} */
  let pending = [];
  /** @type {number} */
  let id = 0;

  function run() {
    processBatch(pending);
    pending = [];
    id = 0;
  }

  return function enqueue(data) {
    id = id || requestAnimationFrame(() => run());
    let { promise, resolve, reject } = Promise.withResolvers();
    pending.push({ data, resolve, reject });
    return promise;
  };
}
