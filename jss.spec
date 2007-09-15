%define name		jss
%define major		3
%define minor		4
%define version		%{major}.%{minor}
%define release		%mkrel 8
%define	section		free
%define build_free	1
%define gcj_support	1

Name:		%{name}
Summary:	Network Security Services for Java (JSS)
Version:	%{version}
Release:	%{release}
Epoch:		0
License:	GPL
Group:		Development/Java
URL:		http://www.mozilla.org/projects/security/pki/jss/
Source0:	ftp://ftp.mozilla.org/pub/mozilla.org/security/jss/releases/JSS_3_4_RTM/src/jss-3.4-src.tar.bz2
Patch0:		jss-3.4-nss-3.11.4.patch
BuildRequires:  java-devel
BuildRequires:  jpackage-utils >= 0:1.5
# For mozilla-firefox-nss.pc
BuildRequires:	libnss-devel
BuildRequires:	nsinstall
%if %{gcj_support}
BuildRequires:    java-gcj-compat-devel
%endif
BuildRoot:	%{_tmppath}/%{name}-%{version}-buildroot

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
%setup -q -n %{name}-%{version}-src/mozilla/security/jss
%patch0 -p4 -b .nss
find . -type d -name CVS | xargs %{__rm} -rf
# Support Linux 2.6
if test x"`uname -s`" = xLinux; then
  %{__rm} -f ../coreconf/Linux2.6.mk
  %{__ln_s} ../coreconf/Linux2.4.mk ../coreconf/Linux2.6.mk
fi
%if %{build_free}
# Don't add Sun provider
%{__perl} -pi -e 's|^(\s*)java.security.Security.addProvider|//\1java.security.Security.addProvider|' \
  org/mozilla/jss/tests/DigestTest.java
# Don't link with libjava or libjvm
%{__perl} -pi -e 's/^(\s*)JAVA_LIBS/#\1JAVA_LIBS/g' ../coreconf/jdk.mk
%endif

%build
export CLASSPATH=
export JAVA_HOME="%{java_home}"
export JCE_JAR=""
%{__make} \
  NSDISTMODE=copy \
  NSINSTALL=%{_bindir}/nsinstall \
  XP_DEFINE="-DXP_UNIX `pkg-config --cflags nss`"
pushd ../../dist/classes_DBG
%{jar} cf %{name}-%{version}.jar .
popd
%{__mkdir_p} ../../dist/javadoc
# FIXME: triggers bug in gjdoc
%if %{build_free}
%{__rm} -f org/mozilla/jss/crypto/{KeyGenAlgorithm,KeyGenerator,PBEAlgorithm}.java
%endif
%{javadoc} -breakiterator -sourcepath . -d ../../dist/jssdoc org.mozilla.jss org.mozilla.jss.asn1 org.mozilla.jss.crypto org.mozilla.jss.pkcs7 org.mozilla.jss.pkcs10 org.mozilla.jss.pkcs11 org.mozilla.jss.pkcs12 org.mozilla.jss.pkix.primitive org.mozilla.jss.pkix.cert org.mozilla.jss.pkix.cmc org.mozilla.jss.pkix.cmmf org.mozilla.jss.pkix.cms org.mozilla.jss.pkix.crmf org.mozilla.jss.provider.java.security org.mozilla.jss.provider.javax.crypto org.mozilla.jss.SecretDecoderRing org.mozilla.jss.ssl org.mozilla.jss.tests org.mozilla.jss.util

%install
%{__rm} -rf %{buildroot}

# jars
%{__mkdir_p} %{buildroot}%{_javadir}
%{__install} -m 644 ../../dist/classes_DBG/jss-%{version}.jar \
        %{buildroot}%{_javadir}/%{name}-%{version}.jar
(cd %{buildroot}%{_javadir} && for jar in *-%{version}*; do %{__ln_s} ${jar} `echo $jar| sed  "s|-%{version}||g"`; done)
(cd %{buildroot}%{_javadir} && %{__ln_s} %{name}-%{version}.jar %{name}%{major}%{minor}.jar)

# jni library
%{__mkdir_p} %{buildroot}%{_jnidir}
%{__install} -m 755 ../../dist/"`uname -s`"*/lib/lib%{name}%{major}.so %{buildroot}%{_jnidir}

# javadoc
%{__mkdir_p} %{buildroot}%{_javadocdir}/%{name}-%{version}
%{__cp} -a jss.html %{buildroot}%{_javadocdir}/%{name}-%{version}
%{__cp} -a ../../dist/jssdoc/* %{buildroot}%{_javadocdir}/%{name}-%{version}
%{__ln_s} %{name}-%{version} %{buildroot}%{_javadocdir}/%{name}

%if %{gcj_support}
%{_bindir}/aot-compile-rpm
%endif

%clean
rm -rf %{buildroot}

%if %{gcj_support}
%post
%{update_gcjdb}

%postun
%{clean_gcjdb}
%endif

%post javadoc
%{__rm} -f %{_javadocdir}/%{name}
%{__ln_s} %{name}-%{version} %{_javadocdir}/%{name}

%postun javadoc
if [ "$1" = "0" ]; then
    %{__rm} -f %{_javadocdir}/%{name}
fi

%files
%defattr(0644,root,root,0755)
%doc org/mozilla/jss/tests samples
%{_javadir}/%{name}-%{version}.jar
%{_javadir}/%{name}.jar
%{_javadir}/%{name}%{major}%{minor}.jar
%attr(0755,root,root) %{_jnidir}/lib%{name}%{major}.so
%if %{gcj_support}
%attr(-,root,root) %{_libdir}/gcj/%{name}
%endif

%files javadoc
%defattr(0644,root,root,0755)
%{_javadocdir}/%{name}-%{version}
%ghost %doc %{_javadocdir}/%{name}

