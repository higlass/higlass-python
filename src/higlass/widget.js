import hglib from "https://esm.sh/higlass@1.12?deps=react@17,react-dom@17,pixi.js@6";

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

async function render({ model, el }) {
  let viewconf = model.get("_viewconf");
  let options = model.get("_options") ?? {};
  let api = await hglib.viewer(el, viewconf, options);

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
}

export default { render };
=======
// import hglib from "https://esm.sh/higlass@1.12?deps=react@17,react-dom@17,pixi.js@6";
import * as hglib from "http://localhost:5173/app/scripts/hglib.jsx";
import { v4 } from "https://esm.sh/@lukeed/uuid@2";

// Make sure plugins are registered and enabled
window.higlassDataFetchersByType = window.higlassDataFetchersByType || {};

function uid() {
  return v4().split("-")[0];
}

/**
 * @template T
 * @param {import("npm:@anyiwdget/types").AnyModel} model
 * @param {unknown} payload
 * @param {{ timeout?: number }} [options]
 * @returns {Promise<{ data: T, buffers: DataView[] }>}
 */
function send(model, payload, { timeout = 3000 } = {}) {
  let uuid = uid();
  return new Promise((resolve, reject) => {
    let timer = setTimeout(() => {
      reject(new Error(`Promise timed out after ${timeout} ms`));
      model.off("msg:custom", handler);
    }, timeout);
    /**
     * @param {{ uuid: string, payload: T }} msg
     * @param {DataView[]} buffers
     */
    function handler(msg, buffers) {
      if (!(msg.uuid === uuid)) return;
      clearTimeout(timer);
      resolve({ data: msg.payload, buffers });
      model.off("msg:custom", handler);
    }
    model.on("msg:custom", handler);
    model.send({ payload, uuid });
  });
}

/**
 * Detects server { server: 'jupyter' }, and creates a custom data entry for it.
 * @example
 * resolveJupyterServers({ views: [{ tracks: { top: [{ server: 'jupyter', tilesetUid: 'abc' }] } }] }, 'jupyter-123')
 * // { views: [{ tracks: { top: [{ tilesetUid: 'abc', data: { type: 'jupyter-123', tilesetUid: 'abc' } }] } }] }
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

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

function createDataFetcherForModel(model) {
  return function createDataFetcher(hgc, dataConfig, pubSub) {
    let config = { ...dataConfig, server: "jupyter" };
    return new hgc.dataFetchers.DataFetcher(config, pubSub, {
      async fetchTiles({ id, server, tileIds }) {
        let { data } = await send(model, { type: "tiles", tileIds });
        let result = hgc.services.tileResponseToData(data, "jupyter", tileIds);
        return result;
      },
      async fetchTilesetInfo({ server, tilesetUid }) {
        assert(server === "jupyter", "must be a jupyter server");
        let url = `${server}-${tilesetUid}`;
        let { data } = await send(model, { type: "tileset_info", tilesetUid });
        return data;
      },
      registerTileset() {
        throw new Error("Not implemented");
      },
    });
  };
}

export default () => {
  let id = `jupyter-${uid()}`;
  return {
    async initialize({ model }) {
      let tsId = model.get("_ts");
      let tsModel = await model.widget_manager.get_model(
        tsId.slice("IPY_MODEL_".length)
      );
      window.higlassDataFetchersByType[tsId] = {
        name: id,
        dataFetcher: createDataFetcherForModel(tsModel),
      };
    },
    async render({ model, el }) {
      let viewconf = model.get("_viewconf");
      let options = model.get("_options") ?? {};
      let resolved = resolveJupyterServers(viewconf, model.get("_ts"));
      let api = await hglib.viewer(el, resolved, options);
    },
  };
};
