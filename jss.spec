%define gcj_support  0
%define major        4

Summary:	Network Security Services for Java (JSS)
Name:		jss
Version:	4.2.6
Release:	3
License:	GPLv2+
Group:		Development/Java
Url:		http://www.mozilla.org/projects/security/pki/jss/
# cvs -z3 -d:pserver:anonymous@cvs-mirror.mozilla.org:/cvsroot export -rJSS_4_2_5_RTM mozilla/security/coreconf
# cvs -z3 -d:pserver:anonymous@cvs-mirror.mozilla.org:/cvsroot export -rJSS_4_2_5_RTM mozilla/security/jss
# mv mozilla jss-4.2.5
# tar cvjf jss-4.2.5.tar.bz2 jss-4.2.5
Source0:	jss-%{version}.tar.gz
Source100:	jss.rpmlintrc

Patch1:         jss-key_pair_usage_with_op_flags.patch
Patch2:         jss-javadocs-param.patch
Patch3:         jss-ipv6.patch
Patch4:         jss-ECC-pop.patch
Patch5:         jss-loadlibrary.patch
Patch6:         jss-ocspSettings.patch
Patch7:         jss-ECC_keygen_byCurveName.patch
Patch8:         jss-VerifyCertificate.patch
Patch9:         jss-bad-error-string-pointer.patch
Patch10:        jss-VerifyCertificateReturnCU.patch
#Patch11:        jss-slots-not-freed.patch
Patch12:        jss-ECC-HSM-FIPS.patch
Patch13:        jss-eliminate-native-compiler-warnings.patch
Patch14:        jss-eliminate-java-compiler-warnings.patch
Patch15:        jss-PKCS12-FIPS.patch
Patch16:        jss-eliminate-native-coverity-defects.patch
Patch17:        jss-PBE-PKCS5-V2-secure-P12.patch
Patch18:        jss-wrapInToken.patch
Patch19:        jss-HSM-manufacturerID.patch
Patch20:        jss-ECC-Phase2KeyArchivalRecovery.patch
Patch21:        jss-undo-JCA-deprecations.patch
Patch22:        jss-undo-BadPaddingException-deprecation.patch
Patch23:        jss-fixed-build-issue-on-F17-or-newer.patch

BuildRequires:	java-rpmbuild
BuildRequires:	nspr-devel
BuildRequires:	nss-devel
%if %{gcj_support}
BuildRequires:	java-gcj-compat-devel
%endif

%description
Network Security Services for Java (JSS) is a Java interface to NSS. It 
supports most of the security standards and encryption technologies 
supported by NSS. JSS also provides a pure Java interface for ASN.1 
types and BER/DER encoding.

%package javadoc
Summary:	Javadoc for %{name}
Group:		Development/Java

%description javadoc
%{summary}.

%prep
%setup -q
%apply_patches

%build
[ -z "$JAVA_HOME" ] && export JAVA_HOME=%{_jvmdir}/java

# Enable compiler optimizations and disable debugging code
BUILD_OPT=1
export BUILD_OPT

# Generate symbolic info for debuggers
XCFLAGS="-g %optflags"
export XCFLAGS

PKG_CONFIG_ALLOW_SYSTEM_LIBS=1
PKG_CONFIG_ALLOW_SYSTEM_CFLAGS=1

export PKG_CONFIG_ALLOW_SYSTEM_LIBS
export PKG_CONFIG_ALLOW_SYSTEM_CFLAGS

NSPR_INCLUDE_DIR=`/usr/bin/pkg-config --cflags-only-I nspr | sed 's/-I//'`
NSPR_LIB_DIR=`/usr/bin/pkg-config --libs-only-L nspr | sed 's/-L//'`

NSS_INCLUDE_DIR=`/usr/bin/pkg-config --cflags-only-I nss | sed 's/-I//'`
NSS_LIB_DIR=`/usr/bin/pkg-config --libs-only-L nss | sed 's/-L//'`

export NSPR_INCLUDE_DIR
export NSPR_LIB_DIR
export NSS_INCLUDE_DIR
export NSS_LIB_DIR

%ifarch x86_64 ppc64 ia64 s390x sparc64 aarch64
USE_64=1
export USE_64
%endif

cp -p mozilla/security/coreconf/Linux2.6.mk mozilla/security/coreconf/Linux3.1.mk 
sed -i -e 's;LINUX2_1;LINUX3_1;' mozilla/security/coreconf/Linux3.1.mk

cp -p mozilla/security/coreconf/Linux3.1.mk mozilla/security/coreconf/Linux3.2.mk 
sed -i -e 's;LINUX3_1;LINUX3_2;' mozilla/security/coreconf/Linux3.2.mk

cp -p mozilla/security/coreconf/Linux3.2.mk mozilla/security/coreconf/Linux3.6.mk
sed -i -e 's;LINUX3_1;LINUX3_6;' mozilla/security/coreconf/Linux3.6.mk

# The Makefile is not thread-safe
make -C mozilla/security/coreconf
make -C mozilla/security/jss
make -C mozilla/security/jss javadoc

%install
rm -rf %{buildroot} docdir

# There is no install target so we'll do it by hand

# jars
install -d -m 0755 %{buildroot}%{_jnidir}
install -m 644 mozilla/dist/xpclass.jar %{buildroot}%{_jnidir}/jss4.jar
install -d -m 0755 %{buildroot}%{_libdir}/jss
install -m 644 mozilla/dist/xpclass.jar %{buildroot}%{_libdir}/jss/jss4-%{version}.jar
ln -fs jss4-%{version}.jar %{buildroot}%{_libdir}/jss/jss4.jar

install -d -m 0755 %{buildroot}%{_jnidir}
ln -fs %{_libdir}/jss/jss4.jar %{buildroot}%{_jnidir}/jss4.jar

# We have to use the name libjss4.so because this is dynamically
# loaded by the jar file.
install -d -m 0755 %{buildroot}%{_libdir}/jss
install -m 0755 mozilla/dist/Linux*.OBJ/lib/libjss4.so %{buildroot}%{_libdir}/jss/
pushd  %{buildroot}%{_libdir}/jss
    ln -fs %{_jnidir}/jss4.jar jss4.jar
popd

# javadoc
install -d -m 0755 %{buildroot}%{_javadocdir}/%{name}-%{version}
cp -rp mozilla/dist/jssdoc/* %{buildroot}%{_javadocdir}/%{name}-%{version}

%if %{gcj_support}
%{_bindir}/aot-compile-rpm
%endif

%if %{gcj_support}
%post
%update_gcjdb

%postun
%clean_gcjdb
%endif

%files
%doc mozilla/security/jss/jss.html
%{_libdir}/jss/*
%{_jnidir}/*
%if %{gcj_support}
%dir  %{_libdir}/gcj/%{name}
%attr(-,root,root) %{_libdir}/gcj/%{name}/*
%endif

%files javadoc
%dir %{_javadocdir}/%{name}-%{version}
%{_javadocdir}/%{name}-%{version}/*
