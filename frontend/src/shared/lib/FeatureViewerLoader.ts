/*   Copyright (c) 2020 Merck Sharp & Dohme Corp. a subsidiary of Merck & Co., Inc., Kenilworth, NJ, USA.
 *
 *   This file is part of the Mutation Maker, An Open Source Oligo Design Software For Mutagenesis and De Novo Gene Synthesis Experiments.
 *
 *   Mutation Maker is free software: you can redistribute it and/or modify
 *   it under the terms of the GNU General Public License as published by
 *   the Free Software Foundation, either version 3 of the License, or
 *   (at your option) any later version.
 *
 *   This program is distributed in the hope that it will be useful,
 *   but WITHOUT ANY WARRANTY; without even the implied warranty of
 *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *   GNU General Public License for more details.
 *
 *   You should have received a copy of the GNU General Public License
 *   along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

let FeatureViewerModule: any = null
let loadPromise: Promise<any> | null = null

export const loadFeatureViewer = async () => {
  if (FeatureViewerModule) {
    return FeatureViewerModule
  }
  
  if (loadPromise) {
    return loadPromise
  }
  
  loadPromise = (async () => {
    const jquery = await import('jquery')
    const d3 = await import('d3')
    
    ;(window as any).jQuery = jquery.default
    ;(window as any).$ = jquery.default
    ;(window as any).d3 = d3
    
    const fvPath = new URL('../../../feature-viewer/src/feature-viewer.js', import.meta.url).href
    const fvModule = await import(/* @vite-ignore */ fvPath)
    
    FeatureViewerModule = fvModule.default || fvModule
    return FeatureViewerModule
  })()
  
  return loadPromise
}

export default loadFeatureViewer
