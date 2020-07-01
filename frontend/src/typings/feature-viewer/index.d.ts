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

declare module 'feature-viewer' {
  export type FeatureViewerOptions = {
    showAxis?: boolean
    showSequence?: boolean
    brushActive?: boolean
    toolbar?: boolean
    bubbleHelp?: boolean
    zoomMax?: number /* multiple of ten */
    units?: string
    animation?: boolean
    offset?: {
      start: number
      end: number
    }
    onMouseEnter?(object: any, index: number): void
    onMouseLeave?(object: any, index: number): void
    onClick?(object: any, index: number): void
  }

  export type FeatureObject = {
    x: number
    y: number
    id?: string
    description?: string
    color?: string
  }

  export type FeatureOptions = {
    data: FeatureObject[]
    name: string
    className: string
    height?: number
    color?: string
    type: 'rect' | 'path' | 'line' | 'arrow' | 'rarrow'
    filter?: string,
    yAxis?: {
      min: string | number
      max: string | number
    }
  }

  export type FeatureSelectedEvent = {
    detail: {
      start: number
      end: number
      id?: string
      description?: string
      context?: {
        minX: number
        maxY: number
      }
    }
  }

  export type ZoomAlteredEvent = {
    detail: {
      start: number
      end: number
      zoom: string | number
    }
  }

  class FeatureViewer {
    constructor(
      sequenceOrLength: string | number,
      elementSelector: string | JQuery<HTMLElement>,
      options?: FeatureViewerOptions,
    )

    addFeature(featureOptions: FeatureOptions): void
    onFeatureSelected(callback: (event: FeatureSelectedEvent) => void): void
    onZoom(callback: (event: ZoomAlteredEvent) => void): void
    resetZoom(): void
    zoom(start: number, end: number): void
    colorFeature(selector: string, color: string): void
    showSelectedBox(x: number, y: number, id: string, backgroundColor?: string): void
    hideSelectedBox(id: string): void
    hideAllSelectedBoxes(): void
  }

  export default FeatureViewer
}
