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

import { Layout, Menu, Button, Card, Col, Row } from 'antd'
import * as React from 'react'
import { Route, RouteComponentProps, Switch, withRouter } from 'react-router'
import { Link } from 'react-router-dom'

import withJobStore, { WithJobStore } from 'shared/components/withJobStore'
import { Workflow } from 'shared/workflow'

import QCLM from 'scenes/QCLM'
import SSM from 'scenes/SSM'
import PAS from 'scenes/PAS'

import './App.css'

type AppInnerProps = WithJobStore & RouteComponentProps<any>

const POLL_INTERVAL = 1000

const getCurrentRootPath = () => {
  const chunks = window.location.pathname.split('/')

  return chunks.length > 1 ? chunks[1] : '/'
}

const App: React.SFC<AppInnerProps> = ({ jobState, getJob, submitRequest, requestJobResult }) => (
  <Layout>
    <Layout.Header>
      <Menu
        theme="dark"
        mode="horizontal"
        defaultSelectedKeys={[getCurrentRootPath()]}
        style={{ lineHeight: '64px' }}>
        <Menu.Item key="ssm">
          <Link to={`/${Workflow.ssm}`}>SSSM</Link>
        </Menu.Item>
        <Menu.Item key="qclm">
          <Link to={`/${Workflow.qclm}`}>MSDM</Link>
        </Menu.Item>
        <Menu.Item key="pas">
          <Link to={`/${Workflow.pas}`}>PAS</Link>
        </Menu.Item>
        <Menu.Item className="version">
          <div>
            <a href="https://github.com/Merck/Mutation_Maker/issues">Report an issue</a>
          </div>
        </Menu.Item>
        <Menu.Item className="version">
          <div>Version: 1.0.0</div>
        </Menu.Item>
      </Menu>
    </Layout.Header>

    <Layout.Content className="container">
      <Switch>
        <Route
          path="/ssm/:id?"
          // tslint:disable-next-line:jsx-no-lambda
          render={(routeParams) => {
            const jobId = routeParams.match.params.id

            return (
              <SSM
                jobId={jobId}
                jobData={getJob(jobId)}
                submitRequest={submitRequest}
                requestJobResult={requestJobResult}
                pollInterval={POLL_INTERVAL}
              />
            )
          }}
        />
        <Route
          exact
          path="/qclm/:id?"
          // tslint:disable-next-line:jsx-no-lambda
          render={(routeParams) => {
            const jobId = routeParams.match.params.id

            return (
              <QCLM
                jobId={jobId}
                jobData={getJob(jobId)}
                submitRequest={submitRequest}
                requestJobResult={requestJobResult}
                pollInterval={POLL_INTERVAL}
              />
            )
          }}
        />
        <Route
          exact
          path="/pas/:id?"
          // tslint:disable-next-line:jsx-no-lambda
          render={(routeParams) => {
            const jobId = routeParams.match.params.id

            return (
              <PAS
                jobId={jobId}
                jobData={getJob(jobId)}
                submitRequest={submitRequest}
                requestJobResult={requestJobResult}
                pollInterval={POLL_INTERVAL}
              />
            )
          }}
        />
        <Route
          exact
          path="/"
          // tslint:disable-next-line:jsx-no-lambda
          render={(routeParams) => {
            return (
              <div className="workflow-cards">
                <Row gutter={24} type="flex" justify="center">
                  <Col md={8} sm={12} xs={24}>
                    <Card
                      className="workflow-card"
                      title="SSSM (Site-Scanning Saturation Mutagenesis)"
                      bordered={false}>
                      <p className="workflow-card-description">
                        Design mutagenic primers for site scanning saturation mutagenesis workflows
                        that enable parallel mutational scan at multiple sites using random amino
                        acid substitutions.
                      </p>

                      <Button type="primary" size="large" href={`/${Workflow.ssm}`}>
                        SSSM
                      </Button>
                    </Card>
                  </Col>
                  <Col md={8} sm={12} xs={24}>
                    <Card
                      className="workflow-card"
                      title="MSDM (Multi Site-Directed Mutagenesis)"
                      bordered={false}>
                      <p className="workflow-card-description">
                        Design mutagenic primers for multi-site directed mutagenesis workflows using
                        the QCLM kit by which specific amino acid changes at multiple sites could be
                        combined simultaneously.
                      </p>

                      <Button type="primary" size="large" href={`/${Workflow.qclm}`}>
                        MSDM
                      </Button>
                    </Card>
                  </Col>
                  <Col md={8} sm={12} xs={24}>
                    <Card
                      className="workflow-card"
                      title="PAS (PCR-based Accurate Synthesis)"
                      bordered={false}>
                      <p className="workflow-card-description">
                        Design mutagenic oligos for PCR-based gene synthesis workflows by
                        which specific amino acids changes could be combined at multiple sites
                        simultaneously via accurate assembly of overlapping synthetic gene
                        fragments.
                      </p>

                      <Button type="primary" size="large" href={`/${Workflow.pas}`}>
                        PAS
                      </Button>
                    </Card>
                  </Col>
                </Row>
              </div>
            )
          }}
        />
      </Switch>
    </Layout.Content>
    <Layout.Footer />
  </Layout>
)

/**
 * `withRouter` is added in order to fix blocked updates (as described here https://github.com/ReactTraining/react-router/blob/master/packages/react-router/docs/guides/blocked-updates.md)
 */
export default withRouter(withJobStore(App))
