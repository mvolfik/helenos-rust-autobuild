import sys


with open("Dockerfile.template", "r") as fh:
    TEMPLATE = fh.read()

CONFIGS = {
    "i686": {
        "HELENOS_TOOLCHAIN": "ia32",
        "HELENOS_TARGET_NAME": "ia32",
        "GCC_TOOLCHAIN": "i686",
        "RUST_TOOLCHAIN": "i686-unknown-helenos",
        "ISO_FILES": "",
    },
    "x86_64": {
        "HELENOS_TOOLCHAIN": "amd64",
        "HELENOS_TARGET_NAME": "amd64",
        "GCC_TOOLCHAIN": "amd64",
        "RUST_TOOLCHAIN": "x86_64-unknown-helenos",
    },
    "aarch64": {
        "HELENOS_TOOLCHAIN": "arm64",
        "HELENOS_TARGET_NAME": "arm64/virt",
        "GCC_TOOLCHAIN": "aarch64",
        "RUST_TOOLCHAIN": "aarch64-unknown-helenos",
    },
    "arm": {
        "HELENOS_TOOLCHAIN": "arm32",
        "HELENOS_TARGET_NAME": "arm32/integratorcp",
        "GCC_TOOLCHAIN": "arm",
        "RUST_TOOLCHAIN": "armv5te-unknown-helenos-eabi",
    },
    "sparc64": {
        "HELENOS_TOOLCHAIN": "sparc64",
        "HELENOS_TARGET_NAME": "sparc64/ultra",
        "GCC_TOOLCHAIN": "sparc64",
        "RUST_TOOLCHAIN": "sparc64-unknown-helenos",
    },
    "powerpc": {
        "HELENOS_TOOLCHAIN": "ppc32",
        "HELENOS_TARGET_NAME": "ppc32",
        "GCC_TOOLCHAIN": "ppc",
        "RUST_TOOLCHAIN": "powerpc-unknown-helenos",
    },
}

BUILD_APP_TEMPLATE = """FROM rust-builder AS app{i}
WORKDIR /app
RUN git clone {app} --depth 1 source
WORKDIR /app/source
RUN /root/.cargo/bin/cargo +custom build --target {RUST_TOOLCHAIN} --bins --release --artifact-dir /app/dist -Zunstable-options

"""

host_platform = "x86_64"


def usage():
    print(
        "Usage: gen.py <arch> [--host <host-platform>] <application>...",
        file=sys.stderr,
    )
    print(
        "Available architectures: x86_64, sparc64, powerpc, aarch64, i686.",
        file=sys.stderr,
    )
    print(
        "Each application should be a https:// URL of a git repository.",
        file=sys.stderr,
    )
    print(
        f"Use --host if your current machine is not {host_platform}, known working variants: aarch64, i686, x86_64.",
        file=sys.stderr,
    )

    sys.exit(1)


if len(sys.argv) < 3:
    usage()

args = iter(sys.argv[1:])

arch = next(args)
if arch == "--host":
    host_platform = next(args)
    arch = next(args)

if arch not in CONFIGS:
    print(f"Unknown architecture: {arch}", file=sys.stderr)
    usage()

apps = []
for arg in args:
    if arg == "--host":
        host_platform = next(args)
        continue

    apps.append(arg)

build_apps = ""

for i, app in enumerate(apps):
    build_apps += BUILD_APP_TEMPLATE.format(**CONFIGS[arch], app=app, i=i)

build_apps += "\nFROM scratch AS apps\n"
for i in range(len(apps)):
    build_apps += f"COPY --from=app{i} /app/dist/* /apps/\n"

print(
    TEMPLATE.format(
        **CONFIGS[arch], host_platform=host_platform, build_apps=build_apps
    ),
    end="",
)
