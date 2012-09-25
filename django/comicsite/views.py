'''
Created on Jun 18, 2012

Testing views. Each of these views is referenced in urls.py 

@author: Sjoerd
'''
import pdb


from django.contrib.admin.options import ModelAdmin
from django.core.urlresolvers import reverse
from django.http import HttpResponse,Http404
from django.shortcuts import render_to_response
from django.template import RequestContext,Context,Template,TemplateSyntaxError


import comicsite.templatetags.template_tags
from comicsite.models import ComicSite,Page,ComicSiteException
from comicsite.admin import ComicSiteAdmin
from dataproviders import FileSystemDataProvider

 

def index(request):
    return  HttpResponse("ComicSite index page.",context_instance=RequestContext(request))


def site(request, site_short_name):
    """ show a single COMIC site, default start page """
    #TODO: Is it bad to use site name here, which is not the specified key?
    
    site = getSite(site_short_name)
                    
    pages = getPages(site_short_name)
    
    if len(pages) == 0:
        page = Page(ComicSite=site,title="no_pages_found",html="No pages found for this site. Please log in and use the admin button to add pages.")
        currentpage = page    
    else:
        currentpage = pages[0]
    
    return render_to_response('page.html', {'site': site, 'currentpage': currentpage, "pages":pages },context_instance=RequestContext(request))
    

def page(request, site_short_name, page_title):
    """ show a single page on a site """
    
    try:
        p = Page.objects.get(ComicSite__short_name=site_short_name, title=page_title)
    except Page.DoesNotExist:                
        raise Http404
    pages = getPages(site_short_name)
    
    # render page contents using django template system
    # This makes it possible to use tags like '{% dataset %}' in page
    
    
    rendererror = ""
    try:
        t = Template("{% load template_tags %}"+p.html)        
    except TemplateSyntaxError as e:        
        rendererror = e.message  
            
    if(rendererror):
        # when page contents cannot be rendered, just display raw contents and include error message on page
        errormsg = "<span class=\"pageError\"> Error rendering template: "+rendererror+" </span>"
        pagecontents = p.html + errormsg
    else:
        pagecontents = t.render(RequestContext(request))
    
    p.html = pagecontents
    
    return render_to_response('page.html', {'site': p.ComicSite, 'currentpage': p, "pages":pages },context_instance=RequestContext(request))

                
    
def dataPage(request):
    """ test function for data provider. Just get some files from provider and show them as list"""
    #= r"D:\userdata\Sjoerd\Aptana Studio 3 Workspace\comic-django\django\static\files"
    
    path = r"D:\userdata\Sjoerd\Aptana Studio 3 Workspace\comic\comic-django\django\static\files"
    dp = FileSystemDataProvider.FileSystemDataProvider(path)
    images = dp.getImages()
    
    htmlOut = "available files:"+", ".join(images)
    p = createTestPage(html=htmlOut)
    
    pages = [p]
    
    return render_to_response('testpage.html', {'site': p.ComicSite, 'currentpage': p, "pages":pages },context_instance=RequestContext(request))

# ======================================== not called directly from urls.py =========================================

def getSite(site_short_name):
    try:
        site = ComicSite.objects.get(short_name=site_short_name)
    except ComicSite.DoesNotExist:                
        raise Http404   
    return site  
    
    
def getPages(site_short_name):
    """ get all pages of the given site from db"""
    try:
        pages = Page.objects.filter(ComicSite__short_name=site_short_name)
    except Page.DoesNotExist:                
        raise Http404
    return pages

# trying to follow pep 0008 here, finally.
def site_exists(site_short_name):
    try:
        site = ComicSite.objects.get(short_name=site_short_name)
        return True
    except ComicSite.DoesNotExist:                
        return False


def comic_site_to_html(comic_site):
     """ Return an html overview of the given ComicSite """
     link = reverse('comicsite.views.site', args=[comic_site.short_name])
     html = create_HTML_a(link,comic_site.short_name)
     
     if comic_site.description !="":
         html += " - " + comic_site.description
         
     img_html = create_HTML_a_img(link,comic_site.logo)
     
     html = "<table><tr valign=\"top\" ><td class = \"thumb\">" + img_html +"</td><td class = \"description\">"+ html + "</td></tr></table>"
     
     html = "<div class = \"comicSiteSummary\">" + html + "</div>"
     return html
    
def create_HTML_a(link_url,link_text):
    return "<a href=\"" + link_url + "\">" +  link_text + "</a>"


def create_HTML_a_img(link_url,image_url):
    """ create a linked image """
    img = "<img src=\"" + image_url + "\">"
    linked_image = create_HTML_a(link_url,img)    
    return linked_image
    
# ======================================================  debug and test ==================================================
def createTestPage(title="testPage",html=""):
    """ Create a quick mockup on the ComicSite 'Test'"""
    
    if site_exists("test"):
        #TODO log a warning here, no exception.
        raise ComicSiteException("I am creating a spoof ComicSite called 'test' on the fly, by a project called 'test' was already defined in DB. This message should be a warning instead of an exception")                
    
    # if no site exists by that name, create it on the fly.
    site = ComicSite()
    site.short_name = "test"
    site.name = "Test Page"
    site.skin = ""
        
    return Page(ComicSite=site,title=title,html=html)
    

def givePageHTML(page):
    return "<h1>%s</h1> <p>%s</p>" %(page.title ,page.html)