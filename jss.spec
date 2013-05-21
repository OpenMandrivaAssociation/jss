%define gcj_support  0
%define major        4

Summary:	Network Security Services for Java (JSS)
Name:		jss
Version:	4.2.5
Release:	4
License:	GPLv2+
Group:		Development/Java
Url:		http://www.mozilla.org/projects/security/pki/jss/
# cvs -z3 -d:pserver:anonymous@cvs-mirror.mozilla.org:/cvsroot export -rJSS_4_2_5_RTM mozilla/security/coreconf
# cvs -z3 -d:pserver:anonymous@cvs-mirror.mozilla.org:/cvsroot export -rJSS_4_2_5_RTM mozilla/security/jss
# mv mozilla jss-4.2.5
# tar cvjf jss-4.2.5.tar.bz2 jss-4.2.5
Source0:	jss-%{version}.tar.bz2
Source100:	jss.rpmlintrc
Patch0:		jss-4.2.5-target_source.patch
Patch1:		http://sources.gentoo.org/viewcvs.py/*checkout*/gentoo-x86/dev-java/jss/files/jss-4.2.5-use_pkg-config.patch
Patch2:		jss-4.2.5-jss-html.patch
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

# XXX:	uses a Sun proprietary API
rm security/jss/org/mozilla/jss/tests/JSSE_SSLClient.java

mkdir -p examples
cp -a security/jss/org/mozilla/jss/ssl/SSL{Client,Server}.java examples

%build
export CLASSPATH=
export JAVA_HOME=%{java_home}
export JAVA_GENTOO_OPTS="-target 1.5 -source 1.5"
%ifarch x86_64 ppc64
export USE_64=1
%endif

cp -p security/coreconf/Linux2.6.mk security/coreconf/Linux3.1.mk 
sed -i -e 's;LINUX2_1;LINUX3_1;' security/coreconf/Linux3.1.mk

cp -p security/coreconf/Linux3.1.mk security/coreconf/Linux3.2.mk 
sed -i -e 's;LINUX3_1;LINUX3_2;' security/coreconf/Linux3.2.mk

cp -p security/coreconf/Linux3.2.mk security/coreconf/Linux3.6.mk
sed -i -e 's;LINUX3_1;LINUX3_6;' security/coreconf/Linux3.6.mk

pushd security/coreconf
%{__make} -j1 BUILD_OPT=1 CC="gcc %{optflags}"
popd
pushd security/jss
%{__make} -j1 BUILD_OPT=1 USE_PKGCONFIG=1 NSS_PKGCONFIG=nss NSPR_PKGCONFIG=nspr CC="gcc %{optflags}"
%{__make} -j1 BUILD_OPT=1 CC="gcc %{optflags}" javadoc
popd

%install
# jars
mkdir -p %{buildroot}%{_jnidir}
install -m 644 dist/xpclass.jar %{buildroot}%{_jnidir}/%{name}-%{version}.jar
(cd %{buildroot}%{_jnidir} && for jar in *-%{version}*; do ln -s ${jar} `/bin/echo ${jar} | sed  "s|-%{version}||g"`; done)
(cd %{buildroot}%{_jnidir} && ln -s %{name}-%{version}.jar jss%{major}-%{version}.jar)
(cd %{buildroot}%{_jnidir} && ln -s jss%{major}-%{version}.jar jss%{major}.jar)

# jni library
mkdir -p %{buildroot}%{_libdir}
install -m 755 security/jss/lib/*/libjss%{major}.so %{buildroot}%{_libdir}

# javadoc
mkdir -p %{buildroot}%{_javadocdir}/%{name}-%{version}
cp -a dist/jssdoc/* %{buildroot}%{_javadocdir}/%{name}-%{version}
ln -s %{name}-%{version} %{buildroot}%{_javadocdir}/%{name}

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
%doc security/jss/jss.html security/jss/samples examples
%{_jnidir}/%{name}-%{version}.jar
%{_jnidir}/%{name}.jar
%{_jnidir}/jss%{major}-%{version}.jar
%{_jnidir}/jss%{major}.jar
%attr(0755,root,root) %{_libdir}/libjss%{major}.so
%if %{gcj_support}
%dir  %{_libdir}/gcj/%{name}
%attr(-,root,root) %{_libdir}/gcj/%{name}/*
%endif

%files javadoc
%{_javadocdir}/%{name}-%{version}
%{_javadocdir}/%{name}

