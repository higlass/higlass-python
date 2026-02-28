// HiGlass's plugin system goes through globals
declare global {
  interface Window {
    higlassDataFetchersByType: Record<string, {
      name: string;
      dataFetcher: PluginDataFetcherConstructor;
    }>;
  }
}

// see https://github.com/higlass/higlass/blob/60dc16ffd31d2ebb86908eaf62e1d36374ae2568/app/scripts/types.ts#L143-L168
type TilesetInfo = Record<string, unknown>;

type TilesRequest = {
  id: string;
  server?: string;
  tileIds: string[];
  options?: unknown;
};

type TilesetInfoRequest = {
  server: string;
  tilesetUid: string;
};

type RegisterTilesetRequest = {
  server: string;
  url: string;
  filetype: string;
  coordSystem?: string;
};

type TileSource<T> = {
  fetchTiles: (request: TilesRequest) => Promise<Record<string, T>>;
  fetchTilesetInfo: (
    request: TilesetInfoRequest,
  ) => Promise<Record<string, TilesetInfo>>;
  registerTileset: (request: RegisterTilesetRequest) => Promise<Response>;
};

export type DataFetcher = {
  // Not available at runtime! (just used to mark the type for typescript)
  _tag: "DataFetcher";
};

export type PluginDataFetcherConstructor = {
  new (
    hgc: HGC,
    config: Record<string, unknown>,
    pubsub: unknown,
  ): DataFetcher;
};

type DataFetcherConstructor = {
  new (
    config: Record<string, unknown>,
    pubsub: unknown,
    // deno-lint-ignore no-explicit-any
    tileSource: TileSource<any>,
  ): DataFetcher;
};

export type HGC = {
  dataFetchers: {
    // see: https://github.com/higlass/higlass/blob/60dc16ffd31d2ebb86908eaf62e1d36374ae2568/app/scripts/data-fetchers/DataFetcher.js#L92
    DataFetcher: DataFetcherConstructor;
  };
  services: {
    // see: https://github.com/higlass/higlass/blob/60dc16ffd31d2ebb86908eaf62e1d36374ae2568/app/scripts/services/worker.js#L386-L403
    tileResponseToData<T>(
      inputData: Record<string, T>,
      server: string,
      tileIds: Array<string>,
    ): Record<string, unknown>;
  };
};

export type GenomicLocation = {
  xDomain: [number, number];
  yDomain: [number, number];
};

/** Partial types for the viewconf */
export type Viewconf = {
  views: Array<
    { uid: string; layout?: unknown; tracks?: unknown }
  >;
};
