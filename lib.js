import hgcss from "higlass/dist/hglib.css";

let styles = Object.assign(
	document.createElement("style"),
	{
		type: "text/css",
		rel: "stylesheet",
		innerText: hgcss,
	}
);

document.getElementsByTagName("head")[0].appendChild(styles)

export * as hglib from "higlass";
