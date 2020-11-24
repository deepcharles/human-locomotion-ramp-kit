import yaml


def preprocess_pip_deps(lines):

    deps = []
    for dep in lines:
        dep = dep.strip()
        if len(dep) == 0 or dep.startswith('#'):
            continue
        # If there is a comment on the same line
        # use this to declare compat with conda install
        deps.append(dep.split('#')[-1].strip())
    return deps


def assert_same_deps(deps_pip, deps_conda):
    a = set(deps_pip)
    b = set(deps_conda)

    missing_conda = a - b
    missing_pip = b - a
    missing = missing_pip + missing_conda

    assert len(missing) == 0, (
        f"Missing dependency {missing_conda} in environment.yml and"
        f"dependencies {missing_pip} in extra_libraries.tst"
    )


if __name__ == '__main__':

    # Load deps from envrionment.yml
    with open('environment.yml') as f:
        conf = yaml.load(f, Loader=yaml.FullLoader)

    deps = conf['dependencies']
    deps = deps[:-1] + deps[-1]['pip']

    with open('requirements.txt') as f:
        deps_pip = preprocess_pip_deps(f.readlines())

    with open('extra_libraries.txt') as f:
        deps_pip += preprocess_pip_deps(f.readlines())

    missing = set(deps_pip).union(deps) - set(deps).intersection(deps_pip)
    missing -= {'pip'}

    assert len(missing) == 0, missing
