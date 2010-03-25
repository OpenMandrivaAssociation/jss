%define gcj_support  1
%define major        4

Name:           jss
Version:        4.2.5
Release:        %mkrel 3.0.5
Epoch:          0
Summary:        Network Security Services for Java (JSS)
License:        GPLv2+
Group:          Development/Java
URL:            http://www.mozilla.org/projects/security/pki/jss/
# cvs -z3 -d:pserver:anonymous@cvs-mirror.mozilla.org:/cvsroot export -rJSS_4_2_5_RTM mozilla/security/coreconf
# cvs -z3 -d:pserver:anonymous@cvs-mirror.mozilla.org:/cvsroot export -rJSS_4_2_5_RTM mozilla/security/jss
# mv mozilla jss-4.2.5
# tar cvjf jss-4.2.5.tar.bz2 jss-4.2.5
Source0:        jss-%{version}.tar.bz2
Patch0:         jss-4.2.5-target_source.patch
Patch1:         http://sources.gentoo.org/viewcvs.py/*checkout*/gentoo-x86/dev-java/jss/files/jss-4.2.5-use_pkg-config.patch
Patch2:         jss-4.2.5-jss-html.patch
BuildRequires:  java-rpmbuild
BuildRequires:  nspr-devel
BuildRequires:  nss-devel
%if %{gcj_support}
BuildRequires:  java-gcj-compat-devel
%endif
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root

%description
Network Security Services for Java (JSS) is a Java interface to NSS. It 
supports most of the security standards and encryption technologies 
supported by NSS. JSS also provides a pure Java interface for ASN.1 
types and BER/DER encoding.

%package javadoc
Summary:        Javadoc for %{name}
Group:          Development/Java

%description javadoc
%{summary}.

%prep
%setup -q
%patch0 -p1
%patch1 -p1
%patch2 -p1

# XXX: uses a Sun proprietary API
%{__rm} security/jss/org/mozilla/jss/tests/JSSE_SSLClient.java

%{__mkdir_p} examples
%{__cp} -a security/jss/org/mozilla/jss/ssl/SSL{Client,Server}.java examples

%build
export CLASSPATH=
export JAVA_HOME=%{java_home}
export JAVA_GENTOO_OPTS="-target 1.5 -source 1.5"
%ifarch x86_64 ppc64
export USE_64=1
%endif
pushd security/coreconf
%{__make} -j1 BUILD_OPT=1 CC="gcc %{optflags}"
popd
pushd security/jss
%{__make} -j1 BUILD_OPT=1 USE_PKGCONFIG=1 NSS_PKGCONFIG=nss NSPR_PKGCONFIG=nspr CC="gcc %{optflags}"
%{__make} -j1 BUILD_OPT=1 CC="gcc %{optflags}" javadoc
popd

%install
%{__rm} -rf %{buildroot}

# jars
%{__mkdir_p} %{buildroot}%{_jnidir}
%{__install} -m 644 dist/xpclass.jar %{buildroot}%{_jnidir}/%{name}-%{version}.jar
(cd %{buildroot}%{_jnidir} && for jar in *-%{version}*; do %{__ln_s} ${jar} `/bin/echo ${jar} | %{__sed}  "s|-%{version}||g"`; done)
(cd %{buildroot}%{_jnidir} && %{__ln_s} %{name}-%{version}.jar jss%{major}-%{version}.jar)
(cd %{buildroot}%{_jnidir} && %{__ln_s} jss%{major}-%{version}.jar jss%{major}.jar)

# jni library
%{__mkdir_p} %{buildroot}%{_libdir}
%{__install} -m 755 security/jss/lib/*/libjss%{major}.so %{buildroot}%{_libdir}

# javadoc
%{__mkdir_p} %{buildroot}%{_javadocdir}/%{name}-%{version}
%{__cp} -a dist/jssdoc/* %{buildroot}%{_javadocdir}/%{name}-%{version}
%{__ln_s} %{name}-%{version} %{buildroot}%{_javadocdir}/%{name}

%if %{gcj_support}
%{_bindir}/aot-compile-rpm
%endif

%if 0
%check
BUILD_OPT=1 %{__perl} security/jss/org/mozilla/jss/tests/all.pl dist dist/Linux*.OBJ/
%endif

%clean
%{__rm} -rf %{buildroot}

%if %{gcj_support}
%post
%{update_gcjdb}

%postun
%{clean_gcjdb}
%endif

%files
%defattr(0644,root,root,0755)
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
%defattr(0644,root,root,0755)
%{_javadocdir}/%{name}-%{version}
%{_javadocdir}/%{name}
