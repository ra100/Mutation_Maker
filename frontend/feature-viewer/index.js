/*
 * feature-viewer
 * https://github.com/calipho-sib/feature-viewer
 *
 * Copyright (c) 2015 Calipho - SIB
 * Licensed under the GNU GPL v2 license.
 */

/**
 @class FeatureViewer
 */

import jQuery from 'jquery'
import * as d3 from 'd3'

global.jQuery = jQuery
global.$ = jQuery
global.d3 = d3

var FeatureViewer = require('./src/feature-viewer.js')

export default FeatureViewer
