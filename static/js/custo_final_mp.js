$(function(){

  function custo_final_change(){
    var custo_embalagem       = parseFloat($("#custo_embalagem").val());
    var qtd_embalagem         = parseFloat($("#qtd_embalagem").val());
    var new_custo_embalagem   = custo_embalagem.toFixed(2);
    var new_qtd_embalagem     = qtd_embalagem.toFixed(2);
    console.log(new_custo_embalagem);
    console.log(new_qtd_embalagem);
    var url_format            = "/custo_final_mp/" + new_custo_embalagem + "/" + new_qtd_embalagem
    console.log(url_format);

    $.ajax({
      type: "GET",
      url: url_format
    }).done(function(data){
      $("#custo_final").attr("value", data.custo_final.toFixed(2))
      $("#custo_final").prop("readonly", true);
    });
  }

  $("#custo_embalagem").change(function(){
    custo_final_change();
  });

  $("#qtd_embalagem").change(function(){
    custo_final_change();
  });

  custo_final_change();
});

