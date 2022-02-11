function toPts({ xDomain, yDomain }) {
	let [x, xe] = xDomain;
	let [y, ye] = yDomain;
	return [x, xe, y, ye];
}

define(["@jupyter-widgets/base"], function (base) {
	// hack to let us use an ES module
	return import("./lib.js").then(({ hglib }) => {

		class HgModel extends base.DOMWidgetModel {}

		class HgView extends base.DOMWidgetView {

			async render() {
				let viewconf = JSON.parse(this.model.get("_viewconf"));
				let api = await hglib.viewer(this.el, viewconf);

				this.model.on('msg:custom', msg => {
					msg = JSON.parse(msg);
					let [fn, ...args] = msg;
					api[fn](...args);
				});

				if (viewconf.views.length === 1) {

					api.on('location', loc => {
						this.model.set('location', toPts(loc))
						this.model.save_changes();
					}, viewconf.views[0].uid);

				} else {

					viewconf.views.forEach((view, idx) => {
						api.on('location', loc => {
							let copy = this.model.get('location').slice();
							copy[idx] = toPts(loc);
							this.model.set('location', copy);
							this.model.save_changes();
						}, view.uid);
					});

				}

			}

		}

		return { HgModel, HgView };
	})
});
