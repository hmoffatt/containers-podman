%global debug_package %{nil}

Name: podman
Epoch: 100
Version: 3.2.3
Release: 1%{?dist}
Summary: Daemon-less container engine for managing containers, pods and images
License: Apache-2.0
URL: https://github.com/containers/podman/releases
Source0: %{name}_%{version}.orig.tar.gz
%if 0%{?suse_version} > 1500 || 0%{?sle_version} > 150000
BuildRequires: timezone
%else
BuildRequires: tzdata
%endif
BuildRequires: golang-1.16
BuildRequires: glibc-static
BuildRequires: glib2-devel
BuildRequires: gpgme-devel
BuildRequires: libassuan-devel
BuildRequires: libgpg-error-devel
BuildRequires: libseccomp-devel
BuildRequires: make
BuildRequires: pkgconfig
BuildRequires: systemd-devel
%if 0%{?suse_version} > 1500 || 0%{?sle_version} > 150000
Requires: timezone
%else
Requires: tzdata
%endif
Requires: catatonit
Requires: conmon
Requires: containernetworking-plugins
Requires: containers-common
Requires: iptables
Requires: libassuan.so.0()(64bit)
Requires: libglib-2.0.so.0()(64bit)
Requires: libgpgme.so.11()(64bit)
Requires: libseccomp.so.2()(64bit)
Requires: libsystemd.so.0()(64bit)
Requires: oci-runtime

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
        -o ./bin/podman ./cmd/podman

%install
install -Dpm755 -d %{buildroot}%{_bindir}
install -Dpm755 -t %{buildroot}%{_bindir}/ bin/podman
DESTDIR=%{buildroot} \
PREFIX=%{_prefix} \
SYSTEMDDIR=%{_unitdir} \
USERSYSTEMDDIR=%{_userunitdir} \
    make install.cni install.completions install.systemd

%files
%license LICENSE
%dir %{_prefix}/share/fish
%dir %{_prefix}/share/fish/vendor_completions.d
%dir %{_sysconfdir}/cni
%dir %{_sysconfdir}/cni/net.d
%{_bindir}/podman
%{_prefix}/share/bash-completion/completions/podman
%{_prefix}/share/bash-completion/completions/podman-remote
%{_prefix}/share/fish/vendor_completions.d/podman-remote.fish
%{_prefix}/share/fish/vendor_completions.d/podman.fish
%{_prefix}/share/zsh/site-functions/_podman
%{_prefix}/share/zsh/site-functions/_podman-remote
%{_sysconfdir}/cni/net.d/87-podman-bridge.conflist
%{_unitdir}/podman-auto-update.service
%{_unitdir}/podman-auto-update.timer
%{_unitdir}/podman.service
%{_unitdir}/podman.socket
%{_userunitdir}/podman-auto-update.service
%{_userunitdir}/podman-auto-update.timer
%{_userunitdir}/podman.service
%{_userunitdir}/podman.socket

%changelog
