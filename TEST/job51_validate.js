var EHRValidate = function(a) {
    var b = {
        mode: "",
        isEn: ""
    };
    $.extend(b, a);
    var c = "divVImage";
    var d = "divVPhrase";
    var e = "divVStep";
    var f = 0;
    var g = "";
    var h = new Array();
    this.succValidate = 0;
    this.clickSourceID = "";
    this.lang = "";
    var i;
    var j = true;
    var k = "";
    var l = 4;
    if (b.isEn == "1") {
        l = 6
    }
    ;this.Refresh = function() {
        if (!j) {
            return
        }
        ;var m;
        j = false;
        k = GetGuid(20, 16);
        $("#hidVGuid").val(k);
        var n = false;
        var o = b.isEn == "0" ? $("#errCheckCodeCN") : $("#errCheckCodeEN");
        var p = b.isEn == "0" ? $("#errCheckCodeCNTxt") : $("#errCheckCodeENTxt");
        var q = b.isEn == "0" ? $("#CheckCodeCNdiv") : $("#CheckCodeENdiv");
        var r = b.isEn == "0" ? "刷新过于频繁，请稍后再试！" : "verification too often";
        if (b.mode == "1") {
            g = $("#hidAccessKey").val();
            m = './ajax/Validate/LoginValidate.aspx?doType=getverify&key=' + g + "&guid=" + k;
            $("#errCheckCodeCN,#errOther").hide();
            q.removeClass("inpList_error");
            hideErrMess(o, p)
        }
        ;$("#" + d + " i,#" + c + " i").css("backgroundImage", "none");
        var s = $("#" + d).html();
        $("#" + d).html(s);
        s = $("#" + c).html();
        $("#" + c).html(s);
        $("#imgPhrase").attr("src", m);
        $("#" + d + " i,#" + c + " i").css("backgroundImage", "url(" + m + ")");
        $("#divLoading").show();
        $('#imgPhrase').load(function() {
            $(this).unbind();
            j = true;
            $("#divLoading").hide()
        });
        $("#imgPhrase").error(function() {
            $(this).unbind();
            j = true;
            if (b.mode == "1") {
                $("#divValidateHtml").hide();
                if (b.isEn == "0") {
                    $("#btnBeginValidate").html("点击完成验证")
                } else {
                    $("#btnBeginValidate").html("Verification")
                }
                ;q.addClass("inpList_error");
                showErrMess(o, p, r, n)
            }
        });
        $("#" + e + " span").hide();
        f = 0;
        h = new Array();
        $("#btnVRefresh").show();
        $("#btnVRefresh").next("span").hide();
        ShowButton();
        if (typeof (i) != "undefined") {
            clearTimeout(i)
        }
    }
    ;
    var GetGuid = function(m, n) {
        var o = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'.split('');
        var p = [], q;
        n = n || o.length;
        if (m) {
            for (q = 0; q < m; q++)
                p[q] = o[0 | Math.random() * n]
        } else {
            var r;
            p[8] = p[13] = p[18] = p[23] = '-';
            p[14] = '4';
            for (q = 0; q < 36; q++) {
                if (!p[q]) {
                    r = 0 | Math.random() * 16;
                    p[q] = o[(q == 19) ? (r & 0x3) | 0x8 : r]
                }
            }
        }
        ;return p.join('')
    };
    var ShowButton = function() {
        if (f == l) {
            $("#btnValidate").addClass("on").css("cursor", "pointer")
        } else {
            $("#btnValidate").removeClass("on").css("cursor", "default")
        }
    };
    this.Init = function() {
        $("#" + e + " span").live("click", function(m) {
            if (!j) {
                return
            }
            ;var n = parseInt($(this).attr("class").replace("yz-step", ""));
            for (var o = n; o <= f; o++) {
                h.pop()
            }
            ;$(this).nextAll("span").hide();
            $(this).hide();
            f = n - 1;
            ShowButton()
        });
        $("#" + c).click(function(m) {
            if (!j) {
                return
            }
            ;var n = window.event ? window.event : m;
            var o = n.srcElement ? n.srcElement : n.target;
            if (f < l && o.className.toString().indexOf("yz-step") == -1) {
                var p = document.documentElement.scrollTop == 0 ? document.body.scrollTop : document.documentElement.scrollTop || document.body.scrollTop;
                var q = document.documentElement.scrollLeft == 0 ? document.body.scrollLeft : document.documentElement.scrollLeft || document.body.scrollLeft;
                var r = parseInt(n.clientX + q - parseInt($(this).offset().left));
                var s = parseInt(n.clientY + p - parseInt($(this).offset().top));
                if (r < 10) {
                    r = 10
                } else if (r > 320) {
                    r = 320
                }
                ;if (s < 10) {
                    s = 10
                } else if (s > 106) {
                    s = 106
                }
                ;var t = true;
                for (var u = 0; u < h.length; u++) {
                    var v = h[u].split(',');
                    if (Math.pow(Math.abs(parseInt(v[0]) - r), 2) + Math.pow(Math.abs(parseInt(v[1]) - s), 2) < 400) {
                        t = false;
                        break
                    }
                }
                ;if (t) {
                    f++;
                    $("#" + e + " .yz-step" + f).show().css({
                        "left": r - 10,
                        "top": s - 10
                    });
                    h.push(r + "," + s);
                    ShowButton()
                }
            }
        });
        if (b.isEn == "0") {
            $("body").click(function(m) {
                if (b.mode == "1") {
                    if (ehr.succValidate == 0) {
                        var n = window.event ? window.event : m;
                        if (n.keyCode == 13) {
                            return
                        }
                        ;var o = n.srcElement ? n.srcElement : n.target;
                        if ($(o).parents("#CheckCodeCNdiv").length > 0 || $(o).attr("id") == "Login_btnLoginCN") {
                            return
                        }
                        ;$("#btnBeginValidate").html("点击完成验证");
                        $("#divValidateHtml").hide()
                    }
                }
            })
        }
        ;if (b.isEn == "1") {
            $("body").click(function(m) {
                if (b.mode == "1") {
                    if (ehr.succValidate == 0) {
                        var n = window.event ? window.event : m;
                        if (n.keyCode == 13) {
                            return
                        }
                        ;var o = n.srcElement ? n.srcElement : n.target;
                        if ($(o).parents("#CheckCodeENdiv").length > 0 || $(o).attr("id") == "Login_btnLoginEN") {
                            return
                        }
                        ;$("#btnBeginValidate").html("Verification");
                        $("#divValidateHtml").hide()
                    }
                }
            })
        }
    }
    ;
    var CodeEnLoad = function() {
        k = GetGuid(20, 16);
        $("#hidVGuid").val(k);
        $("#imgCheckCodeEN").attr("src", "./CommonPage/RandomNumber.aspx?type=login&guid=" + k)
    };
    this.ValidateResult = function() {
        if (f != l) {
            return
        }
        ;var m;
        if (b.mode == "1") {
            m = "./ajax/Validate/LoginValidate.aspx"
        }
        ;$.ajax({
            url: m,
            type: "POST",
            async: true,
            dataType: "xml",
            data: "dotype=checkverift&key=" + g + "&p=" + h.join(";") + "&guid=" + k,
            success: function(n) {
                var o = $(n).find("msgtype").eq(0).text();
                var p = $(n).find("result").eq(0).text();
                if (p == "1") {
                    if (b.mode == "1") {
                        $("#divValidateHtml").css("display", "none");
                        $("#btnBeginValidate").css("display", "none");
                        $("#btnEndValidate").show();
                        ehr.succValidate = 1;
                        if (ehr.clickSourceID != "") {
                            $("#" + ehr.clickSourceID).click()
                        }
                    }
                } else {
                    $("#btnVRefresh").next("span").show();
                    i = setTimeout("ehr.Refresh();", 1000);
                    $("#btnVRefresh").hide();
                    f = 0;
                    ShowButton()
                }
            }
        })
    }
};
$(function() {
    ehr.Init();
    $("#btnBeginValidate").click(function() {
        $("#divValidateHtml").show();
        if (ehr.lang == "en")
            $(this).text("Verifying");
        else
            $(this).text("正在验证");
        ehr.Refresh()
    });
    $("#btnValidate").click(function() {
        ehr.ValidateResult()
    });
    $("#btnVRefresh").click(function() {
        ehr.Refresh()
    })
});
