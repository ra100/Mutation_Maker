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

import FeatureViewer, { FeatureViewerOptions } from 'feature-viewer'
import * as R from 'ramda'
import * as React from 'react'
import { v4 as uuidv4 } from 'uuid'
import { Boundaries, combinedBoundaries } from 'shared/boundaries'
import { WithSelectedAndHighlighted } from 'shared/components/withSelectedAndHighlighted'
import FeatureViewerTheme from 'shared/FeatureViewerTheme'
import { parseMutation } from 'shared/genes'
import { notUndefined } from 'shared/helpers'
import './styles.css'

const featureViewerOptions: FeatureViewerOptions = {
  showAxis: true,
  showSequence: true,
  brushActive: true, // zoom
  toolbar: true, // current zoom & mouse position
  bubbleHelp: true,
  zoomMax: 10, // define the maximum range of the zoom
}

type FeatureViewerComponentProps = {
  geneSequence: string
  geneOffset: number
  scrollOffset?: number
  initializeFeatureViewer(
    componentId: string,
    options: FeatureViewerOptions | undefined,
  ): FeatureViewer
  getBoundaries(identifier: string): Boundaries | undefined
  onClick(dataObject: any): void
  onMouseEnter(dataObject: any): void
  onMouseLeave(dataObject: any): void
} & Pick<WithSelectedAndHighlighted, 'selected' | 'highlighted'>

type FeatureViewerComponentState = {
  featureViewer?: FeatureViewer
  zoom?: { start: number; end: number }
  lastSelectedBoundaries?: { left: number | undefined; right: number | undefined }
}

const selectBoxId = (identifier: string) => `selectbox-${identifier}`

const showSelectBox = (featureViewer: FeatureViewer) => (
  offset: number,
  mutation: string,
  backgroundColor?: string,
) => {
  const parsedMutation = parseMutation(mutation)

  if (parsedMutation) {
    const mutationCoordinate = offset + parsedMutation.position * 3

    featureViewer.showSelectedBox(
      mutationCoordinate - 2,
      mutationCoordinate,
      selectBoxId(mutation),
      backgroundColor,
    )
  }
}

class FeatureViewerComponent extends React.Component<
  FeatureViewerComponentProps,
  FeatureViewerComponentState
> {
  componentId = `fv-${uuidv4()}`
  el: HTMLDivElement | null = null

  state: FeatureViewerComponentState = {}

  initializeFeatureViewer = (componentId: string) => {
    const { geneSequence, initializeFeatureViewer } = this.props

    const featureViewerOptionsWithHandlers = {
      ...featureViewerOptions,
      onClick: this.props.onClick,
      onMouseEnter: this.props.onMouseEnter,
      onMouseLeave: this.props.onMouseLeave,
    }

    const featureViewer = initializeFeatureViewer(componentId, featureViewerOptionsWithHandlers)

    featureViewer.onZoom(({ detail }) => {
      this.setState({ zoom: { start: detail.start + 1, end: detail.end } })
    })

    this.setState({
      featureViewer,
      zoom: {
        start: 1,
        end: geneSequence.length,
      },
    })
  }

  componentDidMount() {
    if (this.el) {
      this.initializeFeatureViewer(this.el.id)
    }
  }

  componentDidUpdate({
    selected: previousSelected,
    highlighted: previousHighlighted,
  }: FeatureViewerComponentProps) {
    const { geneOffset, getBoundaries, selected, highlighted } = this.props

    /* TODO handle change of mutations and primerGroups */

    const { featureViewer, lastSelectedBoundaries } = this.state

    if (featureViewer) {
      /* Zoom handling for selected / deselected identifiers */
      if (!R.isEmpty(previousSelected) && R.isEmpty(selected)) {
        featureViewer.resetZoom()
        this.setState({ lastSelectedBoundaries: undefined })
      } else {
        const selectedBoundaries = combinedBoundaries(
          selected.map(getBoundaries).filter(notUndefined),
        )

        if (!R.equals(lastSelectedBoundaries, selectedBoundaries)) {
          if (selectedBoundaries) {
            featureViewer.zoom(selectedBoundaries.left - 1, selectedBoundaries.right + 1)
            this.setState({ lastSelectedBoundaries: selectedBoundaries })
          } else {
            this.setState({ lastSelectedBoundaries: undefined })
          }
        }
      }

      /* restore default looks for previous identifiers */
      const toDefault = R.union(previousHighlighted, previousSelected)

      toDefault.forEach((identifier) => {
        featureViewer.colorFeature(`.${identifier}`, FeatureViewerTheme.default)
        featureViewer.hideSelectedBox(selectBoxId(identifier))
      })

      /* apply new looks */
      const selectedAndHighlightedIdentifiers = R.difference(
        R.intersection(highlighted, selected),
        R.intersection(previousHighlighted, previousSelected),
      )

      selectedAndHighlightedIdentifiers.forEach((identifier) => {
        featureViewer.colorFeature(`.${identifier}`, FeatureViewerTheme.selectedAndHighlighted)
        showSelectBox(featureViewer)(
          geneOffset,
          identifier,
          FeatureViewerTheme.selectedAndHighlighted,
        )
      })

      const highlightedIdentifiers = R.difference(highlighted, selectedAndHighlightedIdentifiers)

      highlightedIdentifiers.forEach((identifier) => {
        featureViewer.colorFeature(`.${identifier}`, FeatureViewerTheme.highlighted)
        showSelectBox(featureViewer)(geneOffset, identifier, FeatureViewerTheme.highlighted)
      })

      const selectedIdentifiers = R.difference(selected, selectedAndHighlightedIdentifiers)

      selectedIdentifiers.forEach((identifier) => {
        featureViewer.colorFeature(`.${identifier}`, FeatureViewerTheme.selected)
        showSelectBox(featureViewer)(geneOffset, identifier, FeatureViewerTheme.selected)
      })
    }
  }

  scrollBy = (modifier: number) => () => {
    const { featureViewer, zoom } = this.state

    if (featureViewer && zoom) {
      const span = zoom.end - zoom.start
      const offset = Math.round(span / 10)

      featureViewer.zoom(zoom.start + modifier * offset, zoom.end + modifier * offset)
    }
  }

  render() {
    return (
      <div className="FeatureViewer">
        <div id={this.componentId} ref={(el) => (this.el = el)} />
        <div className="FeatureViewer--hint">Right click to reset zoom</div>
      </div>
    )
  }
}

export default FeatureViewerComponent
