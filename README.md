This is a demonstration of how use the frontend user interface of the
[Concourse CI system](http://www.concourse.ci/) independently of the rest
of Concourse.

Be aware that this is a hack and not supported by the Concourse developers.

For normal use cases it's better to use the Concourse CI system as its
developers intended. But certain limits in Concourse mean that adapting
existing processes to use the Concourse CI system as a whole can be a huge
hack. The limits I'm talking about are:

  - the build process must be controlled by Concourse.
  - the build process must run in a container on an OS supported by the
    [Garden](https://github.com/cloudfoundry-incubator/garden) container
    management system. At the time of writing this limited to you Linux,
    or Windows, effectively.
  - the Concourse UI only scales to hundreds of individual components,
    more than that and your web browser becomes unusably slow.
  - your process must fit the Concourse model of "input resources", "tasks"
    and "output resources"

Using generic-concourse-ui you can adapt the nice UI of Concourse without
having to contort your processes to match Concourse's expectations.

An instance of this may be running at:

  <http://generic-concourse-ui.herokuapp.com/>

All code is distributed under the same license as Concourse: Apache 2.0.
