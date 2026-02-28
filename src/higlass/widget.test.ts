import { expect, onTestFinished, test, vi } from "vitest";
import type { AnyModel, Experimental } from "@anywidget/types";
import type { State } from "./widget.js";

const experimental: Experimental = {
  invoke() {
    throw new Error("experimental.invoke is not implemented.");
  },
};

test("render creates a HiGlass viewer with a simple viewconf", async () => {
  const { default: widget } = await import("./widget.js");

  const el = document.createElement("div");
  el.style.width = "800px";
  el.style.height = "400px";
  document.body.appendChild(el);
  onTestFinished(() => el.remove());

  const tilesetModel = {
    on: vi.fn(),
    off: vi.fn(),
    send: vi.fn(),
  };

  const model: AnyModel<State> = {
    get(key) {
      const state: State = {
        _plugin_urls: [],
        _viewconf: {
          views: [{
            uid: "v",
            layout: { x: 0, y: 0, w: 12, h: 6 },
            tracks: {
              top: [{ type: "top-axis", uid: "t" }],
              center: [],
              left: [],
              right: [],
              bottom: [],
            },
          }],
        },
        _options: {},
        _tileset_client: "IPY_MODEL_fake",
        location: [0, 0, 0, 0],
      };
      return state[key];
    },
    set: vi.fn(),
    save_changes: vi.fn(),
    on: vi.fn(),
    off: vi.fn(),
    send: vi.fn(),
    widget_manager: {
      get_model: vi.fn().mockResolvedValue(tilesetModel),
    },
  };

  const cleanup = await widget.render({ model, el, experimental });

  // resolved without throwing; container has content
  expect(el.children.length).toBeGreaterThan(0);

  expect(typeof cleanup).toBe("function");
  cleanup?.();
});
