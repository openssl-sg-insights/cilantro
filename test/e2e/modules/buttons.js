var elements = require("../util/elements");

var EC = protractor.ExpectedConditions;

var Buttons = function() {

    this.startImport = function() {
        return elements.home.startBtn.click;
    };

    this.proceed = function() {
        browser.wait(EC.visibilityOf(elements.publish.proceedBtn));
        return elements.publish.proceedBtn.click;
    };

    this.uploadPub = function() {
        return elements.publish.uploadBtn.click;
    };


    this.restart = function() {
        browser.wait(EC.visibilityOf(elements.navbar.restart));
        return elements.navbar.restart.click;
    };

    this.confirmRestart = function() {
        browser.wait(EC.visibilityOf(elements.restart.confirmBtn));
        return elements.restart.confirmBtn.click;
    };


    this.addArticle = function() {
        return elements.article.addBtn.click;
    };

    this.confirmArticle = function() {
        return elements.article.confirmBtn.click;
    };

    this.dismissArticle = function() {
        return elements.article.dismissBtn.click;
    };

    this.deleteArticle = function() {
        browser.wait(EC.visibilityOf(elements.article.deleteBtn));
        return elements.article.deleteBtn.click;
    };


    this.zenonMarkMissing = function() {
        return elements.zenon.markMissing.click;
    };

    this.zenonReportMissing = function() {
        return elements.zenon.reportMissing.click;
    };

    this.zenonDownloadXML = function() {
        return elements.zenon.downloadLink.click;
    };



};

module.exports = new Buttons();
