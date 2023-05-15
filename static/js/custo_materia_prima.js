$(function(){

  function custo_materia_prima_change(){
    var id_materia_prima = $("#materia_prima").val();
    var qtd_materia_prima = parseFloat($("#qtd_materia_prima").val());
    var new_qtd_materia_prima = qtd_materia_prima.toFixed(2);
    var url_format = "/custo_materia_prima/" + id_materia_prima + "/" + new_qtd_materia_prima

    $.ajax({
      type: "GET",
      url: url_format
    }).done(function(data){
      $("#custo_material").attr("value", data.custo_mp.toFixed(2))
      $("#custo_material").prop("readonly", true);
    });
  }

  $("#qtd_materia_prima").change(function(){
    custo_materia_prima_change();
  });

  custo_materia_prima_change();
});

