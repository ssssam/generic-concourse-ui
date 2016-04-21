#!/usr/bin/python3

import bottle
import networkx
import networkx.readwrite.json_graph

import json
import os


@bottle.route('/dependencies')
def dependencies():
    # In reality, this has do some parsing of Plink Makefiles and
    # the Debian package metadata to get a real idea of the dependencies.
    pass


@bottle.route('/messagequeue-port')
def messagequeue_port():
    pass


class ConcourseShim(object):
    # Concourse UI can display multiple groups of pipelines. They are listed
    # in a row along the top of the window. We assume there's just one group,
    # for now.
    _default_group = "builds"

    def _pipeline(self, pipeline_name, job_names):
        '''Return Concourse-compatible JSON for a single Pipeline.

        A Pipeline contains multiple Jobs. I'm not really sure how
        Groups fit in, but we only have 1 anyway.

        '''
        return dict(
            name=pipeline_name,
            url='/pipelines/%s' % pipeline_name,
            paused=False,
            groups=[
                dict(
                    name=self._default_group,
                    jobs=job_names,
                )
            ])

    def _job(self, pipeline_name, job_name, dependee_jobs):
        '''Return Concourse-compatible JSON for a single Job instance.

        A Job (or task) is some work that needs to be done. Compiling some
        source code is a Job, for example.

        '''
        def source_resource():
            return dict(name="input", resource="input")


        def output_resource(input_names):
            if len(input_names) > 0:
                return dict(name="output", resource="output", passed=input_names)
            else:
                return dict(name="output", resource="output")

        inputs = [source_resource()]

        if dependee_jobs:
            inputs.append(output_resource(dependee_jobs))

        return dict(
            name=job_name,
            url='/pipelines/%s/jobs/%s' % (pipeline_name, job_name),
            next_build=None,
            finished_build=None,
            inputs=inputs,
            outputs=[output_resource([])],
            groups=[self._default_group]
        )

    def _resource(self, pipeline_name, resource_name, resource_type):
        '''Return Concourse-compatible JSON for a single Resource instance.

        A Resource is a generic input or output thing, such as a Git repository
        that provides source code, or a package repository that contains build
        output.

        When using only the UI of Concourse, resources aren't that interesting.

        '''
        return dict(
            name=resource_name,
            type=resource_type,
            groups=[],
            url="/pipelines/%s/resources/%s" % (pipeline_name, resource_name),
        )

    def pipelines(self):
        # Return a single pipeline called "main", containing all jobs.
        nodes = self.build_graph.nodes(data=True)
        all_job_names = [node_data['name'] for node_id, node_data in nodes]
        pipeline = self._pipeline("main", all_job_names)
        return json.dumps(pipeline)

    def pipeline_jobs(self, pipeline):
        # List all the jobs we know about.
        jobs = []
        for job_node_id, job_node_data in self.build_graph.nodes(data=True):
            job_name = job_node_data['name']

            # sorry
            input_edges = self.build_graph.in_edges(job_node_id)
            input_node_ids = [edge[0] for edge in input_edges]
            input_job_names = [self.build_graph.node[i]['name'] for i in
                                input_node_ids]

            job = self._job(pipeline, job_name, input_job_names)
            jobs.append(job)

        return json.dumps(jobs)

    def pipeline_resources(self, pipeline):
        resources = [self._resource(pipeline, name, type)
                     for name, type in
                     [("input", "git"), ("output", "github-release")]]
        return json.dumps(resources)

    def __init__(self, build_graph_node_link_data):
        self.build_graph = networkx.readwrite.json_graph.node_link_graph(
            build_graph_node_link_data)

        self.app = bottle.Bottle()
        self.app.route('/pipelines')(self.pipelines)
        self.app.route('/pipelines/<pipeline>/jobs')(self.pipeline_jobs)
        self.app.route('/pipelines/<pipeline>/resources')(self.pipeline_resources)


def main():
    GRAPH = 'build-graph.json'

    PORT = os.environ.get('PORT', 8080)

    with open(GRAPH) as f:
        build_graph = json.load(f)

    concourse_shim = ConcourseShim(build_graph)

    # API requests under /api/v1/ go to the Concourse shim
    root = bottle.Bottle()
    root.mount('/api/v1', concourse_shim.app)

    # Everything else is treated as a file path, in the parent directory
    # (so we can get at Concourse ATC's files inside the ../atc/ submodule.
    @root.route('/<filepath:path>')
    def serve_file(filepath):
        return bottle.static_file(filepath, root='..')

    bottle.run(root, port=PORT)


main()
