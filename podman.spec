%global debug_package %{nil}

Name: podman
Epoch: 100
Version: 4.0.3
Release: 1%{?dist}
Summary: Daemon-less container engine for managing containers, pods and images
License: Apache-2.0
URL: https://github.com/containers/podman/tags
Source0: %{name}_%{version}.orig.tar.gz
BuildRequires: glib2-devel
BuildRequires: glibc-static
BuildRequires: golang-1.19
BuildRequires: gpgme-devel
BuildRequires: libassuan-devel
BuildRequires: libgpg-error-devel
BuildRequires: libseccomp-devel
BuildRequires: make
BuildRequires: pkgconfig
BuildRequires: systemd-devel
BuildRequires: tzdata
Requires: catatonit
Requires: conmon
Requires: containernetworking-plugins
Requires: containers-common
Requires: iptables
Requires: oci-runtime
Requires: tzdata

%description
Podman is a container engine for managing pods, containers, and
container images. It is a standalone tool and it directly manipulates
containers without the need of a container engine daemon. Podman is able
to interact with container images create in buildah, cri-o, and skopeo,
as they all share the same datastore backend.

%prep
%autosetup -T -c -n %{name}_%{version}-%{release}
tar -zx -f %{S:0} --strip-components=1 -C .

%build
mkdir -p bin
set -ex && \
    export CGO_ENABLED=1 && \
    go build \
        -mod vendor -buildmode pie -v \
        -ldflags "-s -w" \
        -tags "netgo osusergo exclude_graphdriver_devicemapper exclude_graphdriver_btrfs containers_image_openpgp seccomp selinux" \
        -o ./bin/podman ./cmd/podman && \
    go build \
        -mod vendor -buildmode pie -v \
        -ldflags "-s -w" \
        -tags "netgo osusergo exclude_graphdriver_devicemapper exclude_graphdriver_btrfs containers_image_openpgp seccomp selinux remote" \
        -o ./bin/podman-remote ./cmd/podman && \
    go build \
        -mod vendor -buildmode pie -v \
        -ldflags "-s -w" \
        -tags "netgo osusergo exclude_graphdriver_devicemapper exclude_graphdriver_btrfs containers_image_openpgp seccomp selinux" \
        -o ./bin/rootlessport ./cmd/rootlessport

%install
install -Dpm755 -d %{buildroot}%{_sysconfdir}/cni/net.d
install -Dpm755 -d %{buildroot}%{_bindir}
install -Dpm755 -d %{buildroot}%{_libexecdir}/podman
install -Dpm644 -T cni/87-podman-bridge.conflist %{buildroot}%{_sysconfdir}/cni/net.d/87-podman.conflist
install -Dpm755 -t %{buildroot}%{_bindir}/ bin/podman
install -Dpm755 -t %{buildroot}%{_bindir}/ bin/podman-remote
install -Dpm755 -t %{buildroot}%{_libexecdir}/podman/ bin/rootlessport
DESTDIR=%{buildroot} \
PREFIX=%{_prefix} \
SYSTEMDDIR=%{_unitdir} \
USERSYSTEMDDIR=%{_userunitdir} \
    make install.completions install.systemd install.docker

%package docker
Summary: Emulate Docker CLI using podman
Requires: podman = %{epoch}:%{version}-%{release}
Conflicts: docker
Conflicts: docker-ce
Conflicts: docker-ce-cli
Conflicts: docker-ee
Conflicts: docker-ee-cli
Conflicts: docker-latest
Conflicts: docker.io
Conflicts: moby-cli
Conflicts: moby-engine

%description docker
This package installs a script named docker that emulates the Docker CLI
by executes podman commands, it also creates links between all Docker
CLI man pages and podman.

%files
%license LICENSE
%dir %{_sysconfdir}/cni
%dir %{_sysconfdir}/cni/net.d
%dir %{_libexecdir}/podman
%dir %{_prefix}/share/fish
%dir %{_prefix}/share/fish/vendor_completions.d
%{_sysconfdir}/cni/net.d/87-podman.conflist
%{_bindir}/podman
%{_bindir}/podman-remote
%{_libexecdir}/podman/rootlessport
%{_prefix}/share/bash-completion/completions/*
%{_prefix}/share/fish/vendor_completions.d/*
%{_prefix}/share/zsh/site-functions/*
%{_unitdir}/*
%{_userunitdir}/*

%files docker
%{_bindir}/docker
%{_usr}/lib/tmpfiles.d/*

%changelog
