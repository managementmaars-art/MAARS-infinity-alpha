export interface WebUIMeta {
  interactiveIds?: string[];
  dynamicTextIds?: string[];
  dynamicImageIds?: string[];
  containerIds?: string[];
}

export function createWebUIMeta(meta?: WebUIMeta): WebUIMeta {
  return {
    interactiveIds: meta && meta.interactiveIds ? meta.interactiveIds.slice() : [],
    dynamicTextIds: meta && meta.dynamicTextIds ? meta.dynamicTextIds.slice() : [],
    dynamicImageIds: meta && meta.dynamicImageIds ? meta.dynamicImageIds.slice() : [],
    containerIds: meta && meta.containerIds ? meta.containerIds.slice() : [],
  };
}
