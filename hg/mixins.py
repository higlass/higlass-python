
from typing import Protocol


class _T(Protocol):
    type: str

    def copy(self) -> '_T':
        ...


class _TypeMixen:

    def multivec(self: _T):
        copy = self.copy()
        copy.type = 'multivec'
        return copy

    def field_1d_heatmap(self: _T):
        copy = self.copy()
        copy.type = '1d-heatmap'
        return copy

    def line(self: _T):
        copy = self.copy()
        copy.type = 'line'
        return copy

    def point(self: _T):
        copy = self.copy()
        copy.type = 'point'
        return copy

    def bar(self: _T):
        copy = self.copy()
        copy.type = 'bar'
        return copy

    def divergent_bar(self: _T):
        copy = self.copy()
        copy.type = 'divergent-bar'
        return copy

    def stacked_interval(self: _T):
        copy = self.copy()
        copy.type = 'stacked-interval'
        return copy

    def gene_annotations(self: _T):
        copy = self.copy()
        copy.type = 'gene-annotations'
        return copy

    def linear_2d_rectangle_domains(self: _T):
        copy = self.copy()
        copy.type = 'linear-2d-rectangle-domains'
        return copy

    def chromosome_labels(self: _T):
        copy = self.copy()
        copy.type = 'chromosome-labels'
        return copy

    def linear_heatmap(self: _T):
        copy = self.copy()
        copy.type = 'linear-heatmap'
        return copy

    def field_1d_value_interval(self: _T):
        copy = self.copy()
        copy.type = '1d-value-interval'
        return copy

    def field_2d_annotations(self: _T):
        copy = self.copy()
        copy.type = '2d-annotations'
        return copy

    def field_2d_chromosome_annotations(self: _T):
        copy = self.copy()
        copy.type = '2d-chromosome-annotations'
        return copy

    def field_2d_chromosome_grid(self: _T):
        copy = self.copy()
        copy.type = '2d-chromosome-grid'
        return copy

    def field_2d_chromosome_labels(self: _T):
        copy = self.copy()
        copy.type = '2d-chromosome-labels'
        return copy

    def field_2d_rectangle_domains(self: _T):
        copy = self.copy()
        copy.type = '2d-rectangle-domains'
        return copy

    def field_2d_tiles(self: _T):
        copy = self.copy()
        copy.type = '2d-tiles'
        return copy

    def arrowhead_domains(self: _T):
        copy = self.copy()
        copy.type = 'arrowhead-domains'
        return copy

    def bedlike(self: _T):
        copy = self.copy()
        copy.type = 'bedlike'
        return copy

    def cross_rule(self: _T):
        copy = self.copy()
        copy.type = 'cross-rule'
        return copy

    def dummy(self: _T):
        copy = self.copy()
        copy.type = 'dummy'
        return copy

    def horizontal_1d_annotations(self: _T):
        copy = self.copy()
        copy.type = 'horizontal-1d-annotations'
        return copy

    def horizontal_1d_heatmap(self: _T):
        copy = self.copy()
        copy.type = 'horizontal-1d-heatmap'
        return copy

    def horizontal_1d_tiles(self: _T):
        copy = self.copy()
        copy.type = 'horizontal-1d-tiles'
        return copy

    def horizontal_1d_value_interval(self: _T):
        copy = self.copy()
        copy.type = 'horizontal-1d-value-interval'
        return copy

    def horizontal_2d_rectangle_domains(self):
        copy = self.copy()
        copy.type = 'horizontal-2d-rectangle-domains'
        return copy

    def horizontal_bar(self):
        copy = self.copy()
        copy.type = 'horizontal-bar'
        return copy

    def horizontal_chromosome_grid(self):
        copy = self.copy()
        copy.type = 'horizontal-chromosome-grid'
        return copy

    def horizontal_chromosome_labels(self):
        copy = self.copy()
        copy.type = 'horizontal-chromosome-labels'
        return copy

    def horizontal_divergent_bar(self):
        copy = self.copy()
        copy.type = 'horizontal-divergent-bar'
        return copy

    def horizontal_gene_annotations(self):
        copy = self.copy()
        copy.type = 'horizontal-gene-annotations'
        return copy

    def horizontal_heatmap(self):
        copy = self.copy()
        copy.type = 'horizontal-heatmap'
        return copy

    def horizontal_line(self):
        copy = self.copy()
        copy.type = 'horizontal-line'
        return copy

    def horizontal_multivec(self):
        copy = self.copy()
        copy.type = 'horizontal-multivec'
        return copy

    def horizontal_point(self):
        copy = self.copy()
        copy.type = 'horizontal-point'
        return copy

    def horizontal_rule(self):
        copy = self.copy()
        copy.type = 'horizontal-rule'
        return copy

    def horizontal_vector_heatmap(self):
        copy = self.copy()
        copy.type = 'horizontal-vector-heatmap'
        return copy

    def image_tiles(self):
        copy = self.copy()
        copy.type = 'image-tiles'
        return copy

    def left_axis(self):
        copy = self.copy()
        copy.type = 'left-axis'
        return copy

    def left_stacked_interval(self):
        copy = self.copy()
        copy.type = 'left-stacked-interval'
        return copy

    def mapbox_tiles(self):
        copy = self.copy()
        copy.type = 'mapbox-tiles'
        return copy

    def osm_2d_tile_ids(self):
        copy = self.copy()
        copy.type = 'osm-2d-tile-ids'
        return copy

    def osm_tiles(self):
        copy = self.copy()
        copy.type = 'osm-tiles'
        return copy

    def raster_tiles(self):
        copy = self.copy()
        copy.type = 'raster-tiles'
        return copy

    def simple_svg(self):
        copy = self.copy()
        copy.type = 'simple-svg'
        return copy

    def square_markers(self):
        copy = self.copy()
        copy.type = 'square-markers'
        return copy

    def top_axis(self):
        copy = self.copy()
        copy.type = 'top-axis'
        return copy

    def top_stacked_interval(self):
        copy = self.copy()
        copy.type = 'top-stacked-interval'
        return copy

    def vertical_1d_annotations(self):
        copy = self.copy()
        copy.type = 'vertical-1d-annotations'
        return copy

    def vertical_1d_heatmap(self):
        copy = self.copy()
        copy.type = 'vertical-1d-heatmap'
        return copy

    def vertical_1d_tiles(self):
        copy = self.copy()
        copy.type = 'vertical-1d-tiles'
        return copy

    def vertical_1d_value_interval(self):
        copy = self.copy()
        copy.type = 'vertical-1d-value-interval'
        return copy

    def vertical_2d_rectangle_domains(self):
        copy = self.copy()
        copy.type = 'vertical-2d-rectangle-domains'
        return copy

    def vertical_bar(self):
        copy = self.copy()
        copy.type = 'vertical-bar'
        return copy

    def vertical_bedlike(self):
        copy = self.copy()
        copy.type = 'vertical-bedlike'
        return copy

    def vertical_chromosome_grid(self: _T):
        copy = self.copy()
        copy.type = 'vertical-chromosome-grid'
        return copy

    def vertical_chromosome_labels(self):
        copy = self.copy()
        copy.type = 'vertical-chromosome-labels'
        return copy

    def vertical_gene_annotations(self):
        copy = self.copy()
        copy.type = 'vertical-gene-annotations'
        return copy

    def vertical_heatmap(self):
        copy = self.copy()
        copy.type = 'vertical-heatmap'
        return copy

    def vertical_line(self):
        copy = self.copy()
        copy.type = 'vertical-line'
        return copy

    def vertical_multivec(self):
        copy = self.copy()
        copy.type = 'vertical-multivec'
        return copy

    def vertical_point(self):
        copy = self.copy()
        copy.type = 'vertical-point'
        return copy

    def vertical_rule(self):
        copy = self.copy()
        copy.type = 'vertical-rule'
        return copy

    def vertical_vector_heatmap(self):
        copy = self.copy()
        copy.type = 'vertical-vector-heatmap'
        return copy

    def viewport_projection_center(self):
        copy = self.copy()
        copy.type = 'viewport-projection-center'
        return copy

    def viewport_projection_horizontal(self):
        copy = self.copy()
        copy.type = 'viewport-projection-horizontal'
        return copy

    def viewport_projection_vertical(self):
        copy = self.copy()
        copy.type = 'viewport-projection-vertical'
        return copy

