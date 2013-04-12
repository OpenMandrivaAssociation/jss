%define gcj_support  0
%define major        4

Name:           jss
Version:        4.2.5
Release:        4
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
Source100:	jss.rpmlintrc
Patch0:         jss-4.2.5-target_source.patch
Patch1:         http://sources.gentoo.org/viewcvs.py/*checkout*/gentoo-x86/dev-java/jss/files/jss-4.2.5-use_pkg-config.patch
Patch2:         jss-4.2.5-jss-html.patch
BuildRequires:  java-rpmbuild
BuildRequires:  nspr-devel
BuildRequires:  nss-devel
%if %{gcj_support}
BuildRequires:  java-gcj-compat-devel
%endif

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
cp -a dist/jssdoc/* %{buildroot}%{_javadocdir}/%{name}-%{version}
%{__ln_s} %{name}-%{version} %{buildroot}%{_javadocdir}/%{name}

%if %{gcj_support}
%{_bindir}/aot-compile-rpm
%endif

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


%changelog
* Wed May 04 2011 Oden Eriksson <oeriksson@mandriva.com> 0:4.2.5-3.0.7mdv2011.0
+ Revision: 665839
- mass rebuild

* Fri Dec 03 2010 Oden Eriksson <oeriksson@mandriva.com> 0:4.2.5-3.0.6mdv2011.0
+ Revision: 606116
- rebuild

* Thu Mar 25 2010 Oden Eriksson <oeriksson@mandriva.com> 0:4.2.5-3.0.5mdv2010.1
+ Revision: 527395
- rebuilt against nss-3.12.6

* Wed Mar 17 2010 Oden Eriksson <oeriksson@mandriva.com> 0:4.2.5-3.0.4mdv2010.1
+ Revision: 523132
- rebuilt for 2010.1

* Wed Sep 02 2009 Christophe Fergeau <cfergeau@mandriva.com> 0:4.2.5-3.0.3mdv2010.0
+ Revision: 425474
- rebuild

* Fri Apr 10 2009 Funda Wang <fwang@mandriva.org> 0:4.2.5-3.0.2mdv2009.1
+ Revision: 365545
- rediff target source patch

* Wed Aug 06 2008 Thierry Vignaud <tv@mandriva.org> 0:4.2.5-3.0.2mdv2009.0
+ Revision: 264756
- rebuild early 2009.0 package (before pixel changes)

* Tue May 06 2008 David Walluck <walluck@mandriva.org> 0:4.2.5-0.0.2mdv2009.0
+ Revision: 201749
- create %%{_libdir} not %%{_jnidir} again
- 4.2.5

* Sat Jan 05 2008 David Walluck <walluck@mandriva.org> 0:3.4-10mdv2008.1
+ Revision: 145644
- allow javadocs to fail so that build passes

  + Olivier Blin <oblin@mandriva.com>
    - restore BuildRoot

  + Thierry Vignaud <tv@mandriva.org>
    - kill re-definition of %%buildroot on Pixel's request

  + Anssi Hannula <anssi@mandriva.org>
    - buildrequire java-rpmbuild, i.e. build with icedtea on x86(_64)
    - remove unnecessary Requires(post) on java-gcj-compat


* Thu Mar 08 2007 Christiaan Welvaart <cjw@daneel.dyndns.org>
+ 2007-03-08 19:34:50 (138458)
- patch0: fix build with separate nss package
- Import jss

* Sun Jun 04 2006 David Walluck <walluck@mandriva.org> 0:3.4-6mdv2007.0
- rebuild for libgcj.so.7

* Mon Feb 06 2006 David Walluck <walluck@mandriva.org> 0:3.4-5mdk
- use standalone nsinstall

* Sun Jan 15 2006 David Walluck <walluck@mandriva.org> 0:3.4-4mdk
- fix path to aot-compile-rpm
- BuildRequires: java-devel

* Fri Oct 28 2005 David Walluck <walluck@mandriva.org> 0:3.4-3mdk
- rebuild

* Tue Sep 13 2005 David Walluck <walluck@mandriva.org> 0:3.4-2mdk
- add compatibility symlink to jss34.jar
- build libjss3.so
- fix javadoc building

* Mon Sep 12 2005 David Walluck <walluck@mandriva.org> 0:3.4-1mdk
- release

