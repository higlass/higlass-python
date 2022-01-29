
from typing import Protocol, Union, Any, Dict

class T(Protocol):
    options: Union[Dict[str, Any], None]
    type: str

    def copy(self) -> 'T':
        ...

class _TrackTypeMixen:


    def multivec(self: T, **kwargs) -> T:
        copy = self.copy()
        copy.type = "multivec"
        if copy.options is None:
            copy.options = kwargs
        else:
            copy.options.update(kwargs)
        return copy

    def heatmap_1d(self: T, **kwargs) -> T:
        copy = self.copy()
        copy.type = "1d-heatmap"
        if copy.options is None:
            copy.options = kwargs
        else:
            copy.options.update(kwargs)
        return copy

    def line(self: T, **kwargs) -> T:
        copy = self.copy()
        copy.type = "line"
        if copy.options is None:
            copy.options = kwargs
        else:
            copy.options.update(kwargs)
        return copy

    def point(self: T, **kwargs) -> T:
        copy = self.copy()
        copy.type = "point"
        if copy.options is None:
            copy.options = kwargs
        else:
            copy.options.update(kwargs)
        return copy

    def bar(self: T, **kwargs) -> T:
        copy = self.copy()
        copy.type = "bar"
        if copy.options is None:
            copy.options = kwargs
        else:
            copy.options.update(kwargs)
        return copy

    def divergent_bar(self: T, **kwargs) -> T:
        copy = self.copy()
        copy.type = "divergent-bar"
        if copy.options is None:
            copy.options = kwargs
        else:
            copy.options.update(kwargs)
        return copy

    def stacked_interval(self: T, **kwargs) -> T:
        copy = self.copy()
        copy.type = "stacked-interval"
        if copy.options is None:
            copy.options = kwargs
        else:
            copy.options.update(kwargs)
        return copy

    def gene_annotations(self: T, **kwargs) -> T:
        copy = self.copy()
        copy.type = "gene-annotations"
        if copy.options is None:
            copy.options = kwargs
        else:
            copy.options.update(kwargs)
        return copy

    def linear_2d_rectangle_domains(self: T, **kwargs) -> T:
        copy = self.copy()
        copy.type = "linear-2d-rectangle-domains"
        if copy.options is None:
            copy.options = kwargs
        else:
            copy.options.update(kwargs)
        return copy

    def chromosome_labels(self: T, **kwargs) -> T:
        copy = self.copy()
        copy.type = "chromosome-labels"
        if copy.options is None:
            copy.options = kwargs
        else:
            copy.options.update(kwargs)
        return copy

    def linear_heatmap(self: T, **kwargs) -> T:
        copy = self.copy()
        copy.type = "linear-heatmap"
        if copy.options is None:
            copy.options = kwargs
        else:
            copy.options.update(kwargs)
        return copy

    def value_interval_1d(self: T, **kwargs) -> T:
        copy = self.copy()
        copy.type = "1d-value-interval"
        if copy.options is None:
            copy.options = kwargs
        else:
            copy.options.update(kwargs)
        return copy

    def annotations_2d(self: T, **kwargs) -> T:
        copy = self.copy()
        copy.type = "2d-annotations"
        if copy.options is None:
            copy.options = kwargs
        else:
            copy.options.update(kwargs)
        return copy

    def chromosome_annotations_2d(self: T, **kwargs) -> T:
        copy = self.copy()
        copy.type = "2d-chromosome-annotations"
        if copy.options is None:
            copy.options = kwargs
        else:
            copy.options.update(kwargs)
        return copy

    def chromosome_grid_2d(self: T, **kwargs) -> T:
        copy = self.copy()
        copy.type = "2d-chromosome-grid"
        if copy.options is None:
            copy.options = kwargs
        else:
            copy.options.update(kwargs)
        return copy

    def chromosome_labels_2d(self: T, **kwargs) -> T:
        copy = self.copy()
        copy.type = "2d-chromosome-labels"
        if copy.options is None:
            copy.options = kwargs
        else:
            copy.options.update(kwargs)
        return copy

    def rectangle_domains_2d(self: T, **kwargs) -> T:
        copy = self.copy()
        copy.type = "2d-rectangle-domains"
        if copy.options is None:
            copy.options = kwargs
        else:
            copy.options.update(kwargs)
        return copy

    def tiles_2d(self: T, **kwargs) -> T:
        copy = self.copy()
        copy.type = "2d-tiles"
        if copy.options is None:
            copy.options = kwargs
        else:
            copy.options.update(kwargs)
        return copy

    def arrowhead_domains(self: T, **kwargs) -> T:
        copy = self.copy()
        copy.type = "arrowhead-domains"
        if copy.options is None:
            copy.options = kwargs
        else:
            copy.options.update(kwargs)
        return copy

    def bedlike(self: T, **kwargs) -> T:
        copy = self.copy()
        copy.type = "bedlike"
        if copy.options is None:
            copy.options = kwargs
        else:
            copy.options.update(kwargs)
        return copy

    def cross_rule(self: T, **kwargs) -> T:
        copy = self.copy()
        copy.type = "cross-rule"
        if copy.options is None:
            copy.options = kwargs
        else:
            copy.options.update(kwargs)
        return copy

    def dummy(self: T, **kwargs) -> T:
        copy = self.copy()
        copy.type = "dummy"
        if copy.options is None:
            copy.options = kwargs
        else:
            copy.options.update(kwargs)
        return copy

    def horizontal_1d_annotations(self: T, **kwargs) -> T:
        copy = self.copy()
        copy.type = "horizontal-1d-annotations"
        if copy.options is None:
            copy.options = kwargs
        else:
            copy.options.update(kwargs)
        return copy

    def horizontal_1d_heatmap(self: T, **kwargs) -> T:
        copy = self.copy()
        copy.type = "horizontal-1d-heatmap"
        if copy.options is None:
            copy.options = kwargs
        else:
            copy.options.update(kwargs)
        return copy

    def horizontal_1d_tiles(self: T, **kwargs) -> T:
        copy = self.copy()
        copy.type = "horizontal-1d-tiles"
        if copy.options is None:
            copy.options = kwargs
        else:
            copy.options.update(kwargs)
        return copy

    def horizontal_1d_value_interval(self: T, **kwargs) -> T:
        copy = self.copy()
        copy.type = "horizontal-1d-value-interval"
        if copy.options is None:
            copy.options = kwargs
        else:
            copy.options.update(kwargs)
        return copy

    def horizontal_2d_rectangle_domains(self: T, **kwargs) -> T:
        copy = self.copy()
        copy.type = "horizontal-2d-rectangle-domains"
        if copy.options is None:
            copy.options = kwargs
        else:
            copy.options.update(kwargs)
        return copy

    def horizontal_bar(self: T, **kwargs) -> T:
        copy = self.copy()
        copy.type = "horizontal-bar"
        if copy.options is None:
            copy.options = kwargs
        else:
            copy.options.update(kwargs)
        return copy

    def horizontal_chromosome_grid(self: T, **kwargs) -> T:
        copy = self.copy()
        copy.type = "horizontal-chromosome-grid"
        if copy.options is None:
            copy.options = kwargs
        else:
            copy.options.update(kwargs)
        return copy

    def horizontal_chromosome_labels(self: T, **kwargs) -> T:
        copy = self.copy()
        copy.type = "horizontal-chromosome-labels"
        if copy.options is None:
            copy.options = kwargs
        else:
            copy.options.update(kwargs)
        return copy

    def horizontal_divergent_bar(self: T, **kwargs) -> T:
        copy = self.copy()
        copy.type = "horizontal-divergent-bar"
        if copy.options is None:
            copy.options = kwargs
        else:
            copy.options.update(kwargs)
        return copy

    def horizontal_gene_annotations(self: T, **kwargs) -> T:
        copy = self.copy()
        copy.type = "horizontal-gene-annotations"
        if copy.options is None:
            copy.options = kwargs
        else:
            copy.options.update(kwargs)
        return copy

    def horizontal_heatmap(self: T, **kwargs) -> T:
        copy = self.copy()
        copy.type = "horizontal-heatmap"
        if copy.options is None:
            copy.options = kwargs
        else:
            copy.options.update(kwargs)
        return copy

    def horizontal_line(self: T, **kwargs) -> T:
        copy = self.copy()
        copy.type = "horizontal-line"
        if copy.options is None:
            copy.options = kwargs
        else:
            copy.options.update(kwargs)
        return copy

    def horizontal_multivec(self: T, **kwargs) -> T:
        copy = self.copy()
        copy.type = "horizontal-multivec"
        if copy.options is None:
            copy.options = kwargs
        else:
            copy.options.update(kwargs)
        return copy

    def horizontal_point(self: T, **kwargs) -> T:
        copy = self.copy()
        copy.type = "horizontal-point"
        if copy.options is None:
            copy.options = kwargs
        else:
            copy.options.update(kwargs)
        return copy

    def horizontal_rule(self: T, **kwargs) -> T:
        copy = self.copy()
        copy.type = "horizontal-rule"
        if copy.options is None:
            copy.options = kwargs
        else:
            copy.options.update(kwargs)
        return copy

    def horizontal_vector_heatmap(self: T, **kwargs) -> T:
        copy = self.copy()
        copy.type = "horizontal-vector-heatmap"
        if copy.options is None:
            copy.options = kwargs
        else:
            copy.options.update(kwargs)
        return copy

    def image_tiles(self: T, **kwargs) -> T:
        copy = self.copy()
        copy.type = "image-tiles"
        if copy.options is None:
            copy.options = kwargs
        else:
            copy.options.update(kwargs)
        return copy

    def left_axis(self: T, **kwargs) -> T:
        copy = self.copy()
        copy.type = "left-axis"
        if copy.options is None:
            copy.options = kwargs
        else:
            copy.options.update(kwargs)
        return copy

    def left_stacked_interval(self: T, **kwargs) -> T:
        copy = self.copy()
        copy.type = "left-stacked-interval"
        if copy.options is None:
            copy.options = kwargs
        else:
            copy.options.update(kwargs)
        return copy

    def mapbox_tiles(self: T, **kwargs) -> T:
        copy = self.copy()
        copy.type = "mapbox-tiles"
        if copy.options is None:
            copy.options = kwargs
        else:
            copy.options.update(kwargs)
        return copy

    def osm_2d_tile_ids(self: T, **kwargs) -> T:
        copy = self.copy()
        copy.type = "osm-2d-tile-ids"
        if copy.options is None:
            copy.options = kwargs
        else:
            copy.options.update(kwargs)
        return copy

    def osm_tiles(self: T, **kwargs) -> T:
        copy = self.copy()
        copy.type = "osm-tiles"
        if copy.options is None:
            copy.options = kwargs
        else:
            copy.options.update(kwargs)
        return copy

    def raster_tiles(self: T, **kwargs) -> T:
        copy = self.copy()
        copy.type = "raster-tiles"
        if copy.options is None:
            copy.options = kwargs
        else:
            copy.options.update(kwargs)
        return copy

    def simple_svg(self: T, **kwargs) -> T:
        copy = self.copy()
        copy.type = "simple-svg"
        if copy.options is None:
            copy.options = kwargs
        else:
            copy.options.update(kwargs)
        return copy

    def square_markers(self: T, **kwargs) -> T:
        copy = self.copy()
        copy.type = "square-markers"
        if copy.options is None:
            copy.options = kwargs
        else:
            copy.options.update(kwargs)
        return copy

    def top_axis(self: T, **kwargs) -> T:
        copy = self.copy()
        copy.type = "top-axis"
        if copy.options is None:
            copy.options = kwargs
        else:
            copy.options.update(kwargs)
        return copy

    def top_stacked_interval(self: T, **kwargs) -> T:
        copy = self.copy()
        copy.type = "top-stacked-interval"
        if copy.options is None:
            copy.options = kwargs
        else:
            copy.options.update(kwargs)
        return copy

    def vertical_1d_annotations(self: T, **kwargs) -> T:
        copy = self.copy()
        copy.type = "vertical-1d-annotations"
        if copy.options is None:
            copy.options = kwargs
        else:
            copy.options.update(kwargs)
        return copy

    def vertical_1d_heatmap(self: T, **kwargs) -> T:
        copy = self.copy()
        copy.type = "vertical-1d-heatmap"
        if copy.options is None:
            copy.options = kwargs
        else:
            copy.options.update(kwargs)
        return copy

    def vertical_1d_tiles(self: T, **kwargs) -> T:
        copy = self.copy()
        copy.type = "vertical-1d-tiles"
        if copy.options is None:
            copy.options = kwargs
        else:
            copy.options.update(kwargs)
        return copy

    def vertical_1d_value_interval(self: T, **kwargs) -> T:
        copy = self.copy()
        copy.type = "vertical-1d-value-interval"
        if copy.options is None:
            copy.options = kwargs
        else:
            copy.options.update(kwargs)
        return copy

    def vertical_2d_rectangle_domains(self: T, **kwargs) -> T:
        copy = self.copy()
        copy.type = "vertical-2d-rectangle-domains"
        if copy.options is None:
            copy.options = kwargs
        else:
            copy.options.update(kwargs)
        return copy

    def vertical_bar(self: T, **kwargs) -> T:
        copy = self.copy()
        copy.type = "vertical-bar"
        if copy.options is None:
            copy.options = kwargs
        else:
            copy.options.update(kwargs)
        return copy

    def vertical_bedlike(self: T, **kwargs) -> T:
        copy = self.copy()
        copy.type = "vertical-bedlike"
        if copy.options is None:
            copy.options = kwargs
        else:
            copy.options.update(kwargs)
        return copy

    def vertical_chromosome_grid(self: T, **kwargs) -> T:
        copy = self.copy()
        copy.type = "vertical-chromosome-grid"
        if copy.options is None:
            copy.options = kwargs
        else:
            copy.options.update(kwargs)
        return copy

    def vertical_chromosome_labels(self: T, **kwargs) -> T:
        copy = self.copy()
        copy.type = "vertical-chromosome-labels"
        if copy.options is None:
            copy.options = kwargs
        else:
            copy.options.update(kwargs)
        return copy

    def vertical_gene_annotations(self: T, **kwargs) -> T:
        copy = self.copy()
        copy.type = "vertical-gene-annotations"
        if copy.options is None:
            copy.options = kwargs
        else:
            copy.options.update(kwargs)
        return copy

    def vertical_heatmap(self: T, **kwargs) -> T:
        copy = self.copy()
        copy.type = "vertical-heatmap"
        if copy.options is None:
            copy.options = kwargs
        else:
            copy.options.update(kwargs)
        return copy

    def vertical_line(self: T, **kwargs) -> T:
        copy = self.copy()
        copy.type = "vertical-line"
        if copy.options is None:
            copy.options = kwargs
        else:
            copy.options.update(kwargs)
        return copy

    def vertical_multivec(self: T, **kwargs) -> T:
        copy = self.copy()
        copy.type = "vertical-multivec"
        if copy.options is None:
            copy.options = kwargs
        else:
            copy.options.update(kwargs)
        return copy

    def vertical_point(self: T, **kwargs) -> T:
        copy = self.copy()
        copy.type = "vertical-point"
        if copy.options is None:
            copy.options = kwargs
        else:
            copy.options.update(kwargs)
        return copy

    def vertical_rule(self: T, **kwargs) -> T:
        copy = self.copy()
        copy.type = "vertical-rule"
        if copy.options is None:
            copy.options = kwargs
        else:
            copy.options.update(kwargs)
        return copy

    def vertical_vector_heatmap(self: T, **kwargs) -> T:
        copy = self.copy()
        copy.type = "vertical-vector-heatmap"
        if copy.options is None:
            copy.options = kwargs
        else:
            copy.options.update(kwargs)
        return copy

    def viewport_projection_center(self: T, **kwargs) -> T:
        copy = self.copy()
        copy.type = "viewport-projection-center"
        if copy.options is None:
            copy.options = kwargs
        else:
            copy.options.update(kwargs)
        return copy

    def viewport_projection_horizontal(self: T, **kwargs) -> T:
        copy = self.copy()
        copy.type = "viewport-projection-horizontal"
        if copy.options is None:
            copy.options = kwargs
        else:
            copy.options.update(kwargs)
        return copy

    def viewport_projection_vertical(self: T, **kwargs) -> T:
        copy = self.copy()
        copy.type = "viewport-projection-vertical"
        if copy.options is None:
            copy.options = kwargs
        else:
            copy.options.update(kwargs)
        return copy
