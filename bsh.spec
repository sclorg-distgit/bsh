%global pkg_name bsh
%{?scl:%scl_package %{pkg_name}}
%{?maven_find_provides_and_requires}

# Copyright (c) 2000-2007, JPackage Project
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the
#    distribution.
# 3. Neither the name of the JPackage Project nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

Name:           %{?scl_prefix}%{pkg_name}
Version:        1.3.0
Release:        29.14%{?dist}
Epoch:          0
Summary:        Lightweight Scripting for Java
License:        (SPL or LGPLv2+) and Public Domain
Source0:        %{pkg_name}-%{version}-src.tar.bz2
#cvs -d:pserver:anonymous@beanshell.cvs.sourceforge.net:/cvsroot/beanshell login
#cvs -z3 -d:pserver:anonymous@beanshell.cvs.sourceforge.net:/cvsroot/beanshell export -r rel_1_3_0_final BeanShell
#tar cjf bsh-1.3.0-src.tar.bz2 BeanShell
Source1:        bsh-1.3.0.pom
Source2:        bsh-bsf-1.3.0.pom

Patch0:         %{pkg_name}-build.patch
Patch1:         %{pkg_name}-xsl-fixes.patch
BuildRequires:  %{?scl_prefix_java_common}ant
BuildRequires:  %{?scl_prefix_java_common}bsf
BuildRequires:  %{?scl_prefix_java_common}tomcat-servlet-3.0-api
BuildRequires:  ImageMagick
Requires:       %{?scl_prefix_java_common}bsf
URL:            http://www.beanshell.org/
BuildArch:      noarch

%description
BeanShell is a small, free, embeddable, Java source interpreter with
object scripting language features, written in Java.  BeanShell
executes standard Java statements and expressions, in addition to
obvious scripting commands and syntax.  BeanShell supports scripted
objects as simple method closures like those in Perl and
JavaScript(tm).  You can use BeanShell interactively for Java
experimentation and debugging or as a simple scripting engine for your
applications.  In short: BeanShell is a dynamically interpreted Java,
plus some useful stuff.  Another way to describe it is to say that in
many ways BeanShell is to Java as Tcl/Tk is to C: BeanShell is
embeddable - You can call BeanShell from your Java applications to
execute Java code dynamically at run-time or to provide scripting
extensibility for your applications.  Alternatively, you can call your
Java applications and objects from BeanShell; working with Java
objects and APIs dynamically.  Since BeanShell is written in Java and
runs in the same space as your application, you can freely pass
references to "real live" objects into scripts and return them as
results.

%package manual
Summary:        Manual for %{pkg_name}
Requires:       %{?scl_prefix}runtime

%description manual
Documentation for %{pkg_name}.

%package javadoc
Summary:        API documentation for %{pkg_name}

%description javadoc
This package provides %{summary}.

%package demo
Summary:        Demo for %{pkg_name}
AutoReqProv:    no
Requires:       %{name} = %{epoch}:%{version}-%{release}

%description demo
Demonstrations and samples for %{pkg_name}.

%package utils
Summary:        %{pkg_name} utilities
Requires:       %{name} = %{epoch}:%{version}-%{release}
Requires:       %{?scl_prefix}jline

%description utils
%{pkg_name} utilities.

%prep
%setup -q -n BeanShell
%{?scl:scl enable %{scl_java_common} %{scl_maven} %{scl} - <<"EOF"}
set -e -x
%patch0 -p1
%patch1 -p1
for j in $(find . -name "*.jar"); do
    mv $j $j.no
done
# remove all CVS files
for dir in `find . -type d -name CVS`; do rm -rf $dir; done
for file in `find . -type f -name .cvsignore`; do rm -rf $file; done
# fix rpmlint spurious-executable-perm warnings
for i in backbutton forwardbutton homebutton remoteconsole upbutton; do
    chmod 644 docs/images/$i.gif
done
%{?scl:EOF}

%build
%{?scl:scl enable %{scl_java_common} %{scl_maven} %{scl} - <<"EOF"}
set -e -x
mkdir -p lib
pushd lib
ln -sf $(build-classpath bsf)
ln -sf $(build-classpath tomcat-servlet-api)
popd
ant="ant -Dant.build.javac.source=1.5"
$ant test dist
(cd docs/faq && $ant)
(cd docs/manual && $ant)
%{?scl:EOF}

%install
%{?scl:scl enable %{scl_java_common} %{scl_maven} %{scl} - <<"SCL_EOF"}
set -e -x
# jars
install -d -m 755 $RPM_BUILD_ROOT%{_javadir}
for mod in '' bsf classpath commands core reflect util; do
    install -p -m 644 dist/%{pkg_name}${mod:+-${mod}}-%{version}.jar \
             $RPM_BUILD_ROOT%{_javadir}/%{pkg_name}${mod:+-${mod}}.jar
done

# poms
install -d -m 755 $RPM_BUILD_ROOT%{_mavenpomdir}
install -pm 644 %{SOURCE1} \
    $RPM_BUILD_ROOT%{_mavenpomdir}/JPP-%{pkg_name}.pom
install -pm 644 %{SOURCE2} \
    $RPM_BUILD_ROOT%{_mavenpomdir}/JPP-%{pkg_name}-bsf.pom

%add_maven_depmap JPP-%{pkg_name}.pom %{pkg_name}.jar -a org.beanshell:%{pkg_name}
%add_maven_depmap JPP-%{pkg_name}-bsf.pom %{pkg_name}-bsf.jar

# manual
find docs -name ".cvswrappers" -exec rm -f {} \;
find docs -name "*.xml" -exec rm -f {} \;
find docs -name "*.xsl" -exec rm -f {} \;
find docs -name "*.log" -exec rm -f {} \;
(cd docs/manual && mv html/* .)
(cd docs/manual && rm -rf html)
(cd docs/manual && rm -rf xsl)
# javadoc
install -d -m 755 $RPM_BUILD_ROOT%{_javadocdir}/%{name}
cp -pr javadoc/* $RPM_BUILD_ROOT%{_javadocdir}/%{name}

# demo
for i in `find tests -name \*.bsh`; do
  perl -p -i -e 's,^\n?#!(/(usr/)?bin/java bsh\.Interpreter|/bin/sh),#!/usr/bin/env %{_bindir}/%{pkg_name},' $i
  if head -1 $i | grep '#!/usr/bin/env %{_bindir}/%{pkg_name}' >/dev/null; then
    chmod 755 $i
  fi
done
chmod 755 tests/Template
cat > one << EOF
#!/bin/sh

EOF
cat tests/Interactive/reload/one >> one
cat one > tests/Interactive/reload/one
rm one
cat > two << EOF
#!/bin/sh

EOF
cat tests/Interactive/reload/two >> two
cat two > tests/Interactive/reload/two
rm two
install -d -m 755 $RPM_BUILD_ROOT%{_datadir}/%{pkg_name}
cp -pr tests $RPM_BUILD_ROOT%{_datadir}/%{pkg_name}
install -d -m 755 $RPM_BUILD_ROOT%{_datadir}/%{pkg_name}/webapps
install -m 644 dist/bshservlet.war $RPM_BUILD_ROOT%{_datadir}/%{pkg_name}/webapps
install -m 644 dist/bshservlet-wbsh.war $RPM_BUILD_ROOT%{_datadir}/%{pkg_name}/webapps

# scripts
install -d $RPM_BUILD_ROOT%{_bindir}

%jpackage_script bsh.Interpreter "\${BSH_DEBUG:+-Ddebug=true}" jline.ConsoleRunner %{pkg_name}:jline %{pkg_name} true
%jpackage_script bsh.Console "\${BSH_DEBUG:+-Ddebug=true}" "" %{pkg_name} %{pkg_name}-console true

cat > $RPM_BUILD_ROOT%{_bindir}/%{pkg_name}doc << EOF
#!/usr/bin/env %{_bindir}/%{pkg_name}
EOF
cat scripts/bshdoc.bsh >> $RPM_BUILD_ROOT%{_bindir}/%{pkg_name}doc
%{?scl:SCL_EOF}

%files -f .mfiles
%doc src/License.txt
%doc src/Changes.html src/README.txt
%{_javadir}/*
%dir %{_datadir}/%{pkg_name}
%{_datadir}/%{pkg_name}/webapps

%files manual
%doc src/License.txt
%doc docs/*

%files javadoc
%doc src/License.txt
%{_javadocdir}/%{name}

%files demo
%doc tests/README.txt tests/Interactive/README
%{_datadir}/%{pkg_name}/*

%files utils
%attr(0755,root,root) %{_bindir}/%{pkg_name}*

%changelog
* Wed Jan 14 2015 Mikolaj Izdebski <mizdebsk@redhat.com> - 0:1.3.0-29.14
- Add requires on SCL filesystem package

* Tue Jan 13 2015 Michael Simacek <msimacek@redhat.com> - 0:1.3.0-29.13
- Mass rebuild 2015-01-13

* Mon Jan 12 2015 Michael Simacek <msimacek@redhat.com> - 0:1.3.0-29.12
- BR/R on packages from rh-java-common

* Wed Jan 07 2015 Michal Srb <msrb@redhat.com> - 1.3.0-29.11
- Migrate to .mfiles

* Tue Jan 06 2015 Michael Simacek <msimacek@redhat.com> - 0:1.3.0-29.10
- Mass rebuild 2015-01-06

* Mon May 26 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 0:1.3.0-29.9
- Mass rebuild 2014-05-26

* Wed Feb 19 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 0:1.3.0-29.8
- Mass rebuild 2014-02-19

* Wed Feb 19 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 0:1.3.0-29.7
- Remove scriplets for updating icon cache

* Tue Feb 18 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 0:1.3.0-29.6
- Mass rebuild 2014-02-18

* Tue Feb 18 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 0:1.3.0-29.5
- Remove requires on java

* Mon Feb 17 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 0:1.3.0-29.4
- Fix requires

* Fri Feb 14 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 0:1.3.0-29.3
- SCL-ize requires and build-requires

* Thu Feb 13 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 0:1.3.0-29.2
- Rebuild to regenerate auto-requires

* Tue Feb 11 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 0:1.3.0-29.1
- First maven30 software collection build

* Fri Dec 27 2013 Daniel Mach <dmach@redhat.com> - 01.3.0-29
- Mass rebuild 2013-12-27

* Thu Oct 24 2013 Mikolaj Izdebski <mizdebsk@redhat.com> - 0:1.3.0-28
- Remove desktop files

* Fri Jul 12 2013 Mikolaj Izdebski <mizdebsk@redhat.com> - 0:1.3.0-27
- Use %%add_maven_depmap instead of legacy macros
- Install versionless javadocs
- Remove old Obsoletes
- Update and format descriptions
- Install license file with manual and javadoc packages
- Fix Requires and BuildRequires on java
- Fix calls to %%jpackage_script

* Wed Jul 10 2013 Mikolaj Izdebski <mizdebsk@redhat.com> - 0:1.3.0-27
- Remove arch-specific conditionals
- Remove group tags
- Remove Requires on jpackage-utils
- Remove Requires on coreutils
- Generate custom scripts with %%jpackage_script
- Install versionless JARs only
- Install POM files to %%{_mavenpomdir}

* Fri Jun 28 2013 Mikolaj Izdebski <mizdebsk@redhat.com> - 0:1.3.0-26
- Rebuild to regenerate API documentation
- Resolves: CVE-2013-1571

* Thu Jun 06 2013 Michal Srb <msrb@redhat.com> - 0:1.3.0-25
- Enable tests
- Fix BR

* Thu Feb 14 2013 Rahul Sundaram <sundaram@fedoraproject.org> - 0:1.3.0-24
- remove vendor tag from desktop file. https://fedorahosted.org/fpc/ticket/247
- clean up spec to follow current guidelines

* Wed Feb 13 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0:1.3.0-23
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Tue Nov 20 2012 David Tardon <dtardon@redhat.com> - 0:1.3.0-22
- Resolves: rhbz#850008 bsh - Should not own /usr/share/maven-fragments
  directory
- Resolves: rhbz#878163 bsh - javadoc subpackage doesn't require
  jpackage-utils
- Resolves: rhbz#878166 bsh: Public Domain not listed in license tag

* Thu Nov  1 2012 Mikolaj Izdebski <mizdebsk@redhat.com> - 0:1.3.0-21
- Add additional maven depmap

* Wed Jul 18 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0:1.3.0-20
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Thu Jan 12 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0:1.3.0-19
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Mon Feb 07 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0:1.3.0-18
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Thu Nov 25 2010 Ville Skyttä <ville.skytta@iki.fi> - 0:1.3.0-17
- Rename -desktop to -utils, move shell scripts and menu entry to it (#417491).
- Bring icon cache scriptlets up to date with current guidelines.
- Use jline in bsh script for command history support.
- Prefer JRE over SDK when finding JVM to invoke in scripts.
- Build with -source 1.5.

* Thu Nov 25 2010 Stanislav Ochotnicky <sochotnicky@redhat.com> - 0:1.3.0-16
- Fix pom filenames (Resolves rhbz#655791)
- Fix xsl errors when building docs

* Sat Jan 9 2010 Alexander Kurtakov <akurtako@redhat.com> 0:1.3.0-15.2
- Drop gcj_support.
- Fix rpmlint warnings.

* Mon Sep 21 2009 Permaine Cheung <pcheung@redhat.com> 0:1.3.0-15.1
- Do not build manual and faq for ppc64 or s390x as the style task is disabled

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0:1.3.0-15
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Mon Feb 23 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0:1.3.0-14
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Wed Jul  9 2008 Tom "spot" Callaway <tcallawa@redhat.com> - 0:1.3.0-13
- drop repotag
- fix license tag

* Mon Mar 10 2008 Permaine Cheung <pcheung@redhat.com> 0:1.3.0-12jpp.3
- Fix bugzilla 436675. Separate menu entry into desktop subpackage.

* Thu Mar 06 2008 Permaine Cheung <pcheung@redhat.com> 0:1.3.0-12jpp.2
- Fix bugzilla 417491. Thanks Ville Skytta for the patch.
- Add menu entry and startup script for bsh desktop.
- Ensure scriptlets exit with zero exit status.

* Tue Feb 19 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 0:1.3.0-12jpp.1
- Autorebuild for GCC 4.3

* Mon Jan 21 2008 Permaine Cheung <pcheung@redhat.com> 0:1.3.0-11jpp.1
- Merge with upstream

* Thu Jul 12 2007 Ralph Apel <r.apel at r-apel.de> 0:1.3.0-11jpp
- Fix aot build
- Add pom and depmap frags
- Restore all jars
- Add webapps

* Fri Mar 16 2007 Permaine Cheung <pcheung@redhat.com> 0:1.3.0-10jpp.1
- Merge with upstream
- Removed unapplied patch and moved buildroot removal from prep to install,
  and other rpmlint cleanup

* Mon Mar 12 2007 Karsten Hopp <karsten@redhat.com> 1.3.0-9jpp.2
- add buildrequirement ant-trax for documentation

* Fri Aug 04 2006 Deepak Bhole <dbhole@redhat.com> 0:1.3.0-9jpp.1
- Added missing requirements

* Sat Jul 22 2006 Jakub Jelinek <jakub@redhat.com> 0:1.3.0-8jpp_3fc
- Rebuilt

* Fri Jul 21 2006 Deepak Bhole <dbhole@redhat.com> 0:1.3.0-8jpp_2fc
- Removing vendor and distribution tags.

* Thu Jul 20 2006 Deepak Bhole <dbhole@redhat.com> 0:1.3.0-8jpp_1fc
- Add conditional native compilation.

* Thu May 04 2006 Ralph Apel <r.apel at r-apel.de> 0:1.3.0-7jpp
- First JPP-1.7 release

* Fri Aug 20 2004 Ralph Apel <r.apel at r-apel.de> 0:1.3.0-6jpp
- Build with ant-1.6.2

* Mon Jan 26 2004 David Walluck <david@anti-microsoft.org> 0:1.3.0-5jpp
- really drop readline patch

* Sun Jan 25 2004 David Walluck <david@anti-microsoft.org> 0:1.3.0-4jpp
- drop readline patch

* Wed Jan 21 2004 David Walluck <david@anti-microsoft.org> 0:1.3.0-3jpp
- port libreadline-java patch to new bsh

* Tue Jan 20 2004 David Walluck <david@anti-microsoft.org> 0:1.3.0-2jpp
- add Distribution tag

* Tue Jan 20 2004 David Walluck <david@anti-microsoft.org> 0:1.3.0-1jpp
- 1.3.0
- remove bsf patch (fixed upstream)
- add epoch to demo package Requires

* Fri Apr 12 2003 David Walluck <david@anti-microsoft.org> 0:1.2-0.b8.4jpp
- fix strange permissions

* Fri Apr 11 2003 David Walluck <david@anti-microsoft.org> 0:1.2-0.b8.3jpp
- rebuild for JPackage 1.5
- add bsf patch

* Sat Feb 01 2003 David Walluck <david@anti-microsoft.org> 1.2-0.b8.2jpp
- remove servlet dependency (if anyone wants to add this as a separate
  package and do the tomcat integration, be my guest)

* Thu Jan 23 2003 David Walluck <david@anti-microsoft.org> 1.2-0.b8.1jpp
- rename to bsh
- add manual
- add Changes.html to %%doc
- add bsh and bshdoc scripts
- add %%dir %%{_datadir}/%%{name} to main package
- correct test interpreter and make bsh files executable

* Mon Jan 21 2002 Guillaume Rousse <guillomovitch@users.sourceforge.net> 1.01-3jpp
- really section macro

* Sun Jan 20 2002 Guillaume Rousse <guillomovitch@users.sourceforge.net> 1.01-2jpp
- additional sources in individual archives
- versioned dir for javadoc
- no dependencies for javadoc package
- stricter dependency for demo package
- section macro

* Tue Dec 18 2001 Guillaume Rousse <guillomovitch@users.sourceforge.net> 1.01-1jpp
- first JPackage release
