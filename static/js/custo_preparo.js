$(function(){

  function custo_preparo_change(){
    var id_preparo = $("#preparo").val();
    var qtd_preparo = parseFloat($("#qtd_preparo").val());
    var new_qtd_preparo = qtd_preparo.toFixed(2);
    var url_format = "/custo_preparo/" + id_preparo + "/" + new_qtd_preparo

    $.ajax({
      type: "GET",
      url: url_format
    }).done(function(data){
      $("#custo_preparo").attr("value", data.custo.toFixed(2))
      $("#custo_preparo").prop("readonly", true);
    });
  }

  $("#qtd_preparo").change(function(){
    custo_preparo_change();
  });

  custo_preparo_change();
});

